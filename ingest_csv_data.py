"""
CSV Data Ingestion Service for PLFS Survey Data
Handles large CSV files (chhv1.csv, cperv1.csv) with batch processing
"""
import pandas as pd
import os
import sys
from pathlib import Path
import yaml
from typing import Dict, Any, List, Optional
import logging
from sqlalchemy import text, inspect
from datetime import datetime

from app.database import SessionLocal, engine
from app.models.dataset import Dataset, DataRecord
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


class CSVDataIngestion:
    """Ingestion service for large CSV files"""
    
    def __init__(self, csv_file: str, config_file: str):
        self.csv_file = Path(csv_file)
        self.config_file = Path(config_file)
        self.db = SessionLocal()
        self.chunk_size = 1000  # Process 1k rows at a time for better compatibility
        
        if not self.csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_file}")
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
    
    def load_config(self) -> Dict[str, Any]:
        """Load dataset configuration from YAML"""
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config['dataset']
    
    def create_table_from_csv(self, table_name: str, sample_df: pd.DataFrame) -> None:
        """Create database table based on CSV structure"""
        # Map pandas dtypes to SQL types
        type_mapping = {
            'int64': 'INTEGER',
            'float64': 'REAL',
            'object': 'TEXT',
            'bool': 'INTEGER',
            'datetime64[ns]': 'TEXT'
        }
        
        columns = []
        for col, dtype in sample_df.dtypes.items():
            sql_type = type_mapping.get(str(dtype), 'TEXT')
            # Sanitize column names for SQL
            safe_col = col.replace(' ', '_').replace('-', '_')
            columns.append(f'"{safe_col}" {sql_type}')
        
        # Add metadata columns
        columns.extend([
            'id INTEGER PRIMARY KEY AUTOINCREMENT',
            'created_at TEXT DEFAULT CURRENT_TIMESTAMP',
            'updated_at TEXT DEFAULT CURRENT_TIMESTAMP'
        ])
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(columns)}
        )
        """
        
        with engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            conn.execute(text(create_table_sql))
            conn.commit()
        
        logger.info(f"Created table '{table_name}' with {len(sample_df.columns)} columns")
    
    def register_dataset(self, config: Dict[str, Any]) -> Dataset:
        """Register dataset in the database"""
        # Check if dataset already exists
        existing = self.db.query(Dataset).filter(
            Dataset.table_name == config['table_name']
        ).first()
        
        # Prepare full config with metadata
        full_config = {
            'schema': config.get('schema', []),
            'source': config.get('source', 'MoSPI'),
            'file_format': 'csv',
            'size_mb': round(self.csv_file.stat().st_size / (1024 * 1024), 2),
            'relationships': config.get('relationships', []),
            'indexes': config.get('indexes', []),
            'access': config.get('access', {})
        }
        
        if existing:
            logger.info(f"Dataset '{config['name']}' already exists, updating...")
            existing.name = config['name']
            existing.description = config['description']
            existing.config = full_config
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            return existing
        
        # Create new dataset
        dataset = Dataset(
            name=config['name'],
            description=config['description'],
            table_name=config['table_name'],
            config=full_config
        )
        
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        
        logger.info(f"Registered dataset '{config['name']}' (ID: {dataset.id})")
        return dataset
    
    def ingest_csv_data(self, table_name: str, progress_callback=None) -> Dict[str, Any]:
        """Ingest CSV data in chunks"""
        logger.info(f"Starting ingestion of {self.csv_file.name}...")
        
        total_rows = 0
        chunk_count = 0
        errors = []
        
        try:
            # Read CSV in chunks
            for chunk_df in pd.read_csv(self.csv_file, chunksize=self.chunk_size):
                chunk_count += 1
                
                # Clean data
                chunk_df = chunk_df.fillna('')  # Replace NaN with empty string
                
                # Sanitize column names
                chunk_df.columns = [col.replace(' ', '_').replace('-', '_') 
                                   for col in chunk_df.columns]
                
                # Insert into database
                # For tables with many columns, insert in smaller batches to avoid SQLite parameter limit
                try:
                    # Use None method for default behavior (row-by-row for SQLite)
                    # This avoids the 999 parameter limit error with wide tables
                    chunk_df.to_sql(
                        name=table_name,
                        con=engine,
                        if_exists='append',
                        index=False,
                        method=None  # Use default method for SQLite compatibility
                    )
                    
                    total_rows += len(chunk_df)
                    
                    if progress_callback:
                        progress_callback(chunk_count, total_rows)
                    
                    if chunk_count % 10 == 0:
                        logger.info(f"  Processed {total_rows:,} rows ({chunk_count} chunks)...")
                
                except Exception as e:
                    error_msg = f"Error in chunk {chunk_count}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    if len(errors) > 10:  # Stop if too many errors
                        break
            
            logger.info(f"✓ Ingestion complete: {total_rows:,} rows inserted")
            
            return {
                'success': True,
                'total_rows': total_rows,
                'chunks_processed': chunk_count,
                'errors': errors
            }
        
        except Exception as e:
            logger.error(f"Critical error during ingestion: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_rows': total_rows,
                'chunks_processed': chunk_count,
                'errors': errors
            }
    
    def create_indexes(self, table_name: str, config: Dict[str, Any]) -> None:
        """Create indexes for better query performance"""
        if 'indexes' not in config:
            return
        
        logger.info("Creating indexes...")
        
        with engine.connect() as conn:
            for idx in config['indexes']:
                try:
                    idx_name = idx['name']
                    columns = ', '.join([f'"{col}"' for col in idx['columns']])
                    
                    create_idx_sql = f"""
                    CREATE INDEX IF NOT EXISTS {idx_name} 
                    ON {table_name} ({columns})
                    """
                    
                    conn.execute(text(create_idx_sql))
                    logger.info(f"  Created index: {idx_name}")
                
                except Exception as e:
                    logger.warning(f"  Could not create index {idx_name}: {e}")
            
            conn.commit()
    
    def run(self) -> Dict[str, Any]:
        """Execute the complete ingestion pipeline"""
        try:
            # Load configuration
            config = self.load_config()
            table_name = config['table_name']
            
            logger.info("="*60)
            logger.info(f"CSV DATA INGESTION: {config['name']}")
            logger.info(f"Source file: {self.csv_file.name}")
            logger.info(f"File size: {self.csv_file.stat().st_size / (1024*1024):.2f} MB")
            logger.info("="*60)
            
            # Step 1: Read sample to understand structure
            logger.info("\n[1/5] Reading CSV sample...")
            sample_df = pd.read_csv(self.csv_file, nrows=1000)
            logger.info(f"  Columns: {len(sample_df.columns)}")
            logger.info(f"  Sample rows: {len(sample_df)}")
            
            # Step 2: Create table
            logger.info("\n[2/5] Creating database table...")
            self.create_table_from_csv(table_name, sample_df)
            
            # Step 3: Register dataset
            logger.info("\n[3/5] Registering dataset...")
            dataset = self.register_dataset(config)
            
            # Step 4: Ingest data
            logger.info("\n[4/5] Ingesting data...")
            result = self.ingest_csv_data(table_name)
            
            if not result['success']:
                return result
            
            # Step 5: Create indexes
            logger.info("\n[5/5] Creating indexes...")
            self.create_indexes(table_name, config)
            
            logger.info("\n" + "="*60)
            logger.info("✓ INGESTION COMPLETE")
            logger.info(f"  Dataset ID: {dataset.id}")
            logger.info(f"  Table: {table_name}")
            logger.info(f"  Rows: {result['total_rows']:,}")
            logger.info("="*60)
            
            return {
                'success': True,
                'dataset_id': dataset.id,
                'table_name': table_name,
                'total_rows': result['total_rows'],
                'config': config
            }
        
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            self.db.close()


def main():
    """Main entry point for CSV ingestion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest CSV data into the database')
    parser.add_argument('--csv', required=True, help='Path to CSV file')
    parser.add_argument('--config', required=True, help='Path to YAML config file')
    
    args = parser.parse_args()
    
    ingestion = CSVDataIngestion(args.csv, args.config)
    result = ingestion.run()
    
    if result['success']:
        print(f"\n✓ Success! Dataset ID: {result['dataset_id']}")
        sys.exit(0)
    else:
        print(f"\n✗ Failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
