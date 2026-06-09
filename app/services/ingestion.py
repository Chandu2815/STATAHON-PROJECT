"""
Data ingestion service for loading datasets
"""
import pandas as pd
import yaml
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import Dataset, DataRecord, CensusData
from app.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestionService:
    """Service for ingesting datasets into the database"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load dataset configuration from YAML file"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    
    def create_dataset(self, config: Dict[str, Any]) -> Dataset:
        """Create dataset metadata entry"""
        dataset_info = config.get('dataset', {})
        
        dataset = Dataset(
            name=dataset_info.get('name'),
            description=dataset_info.get('description'),
            table_name=dataset_info.get('table_name'),
            config=dataset_info
        )
        
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        
        logger.info(f"Created dataset: {dataset.name}")
        return dataset
    
    def ingest_csv(self, file_path: str, dataset_id: int, batch_size: int = 1000):
        """Ingest data from CSV file"""
        logger.info(f"Reading CSV file: {file_path}")
        df = pd.read_csv(file_path)
        
        total_rows = len(df)
        logger.info(f"Total rows to ingest: {total_rows}")
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')
        
        # Insert in batches
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            data_records = [
                DataRecord(dataset_id=dataset_id, data=record)
                for record in batch
            ]
            
            self.db.bulk_save_objects(data_records)
            self.db.commit()
            
            logger.info(f"Ingested batch {i // batch_size + 1}: {len(batch)} records")
        
        logger.info(f"Successfully ingested {total_rows} records")
    
    def ingest_census_data(self, file_path: str, batch_size: int = 1000):
        """Ingest census-specific data into dedicated table"""
        logger.info(f"Reading census CSV file: {file_path}")
        df = pd.read_csv(file_path)
        
        total_rows = len(df)
        logger.info(f"Total census rows to ingest: {total_rows}")
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')
        
        # Insert in batches
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            census_records = [
                CensusData(**record)
                for record in batch
            ]
            
            self.db.bulk_save_objects(census_records)
            self.db.commit()
            
            logger.info(f"Ingested census batch {i // batch_size + 1}: {len(batch)} records")
        
        logger.info(f"Successfully ingested {total_rows} census records")
    
    def ingest_from_config(self, config_path: str, data_path: str):
        """Complete ingestion workflow using config file"""
        # Load configuration
        config = self.load_config(config_path)
        
        # Create dataset
        dataset = self.create_dataset(config)
        
        # Ingest data
        self.ingest_csv(data_path, dataset.id)
        
        return dataset
    
    def __del__(self):
        if self.db:
            self.db.close()


def main():
    """CLI entry point for data ingestion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Ingestion Service')
    parser.add_argument('--config', required=True, help='Path to dataset config YAML')
    parser.add_argument('--data', required=True, help='Path to data CSV file')
    
    args = parser.parse_args()
    
    service = DataIngestionService()
    dataset = service.ingest_from_config(args.config, args.data)
    print(f"✓ Successfully ingested dataset: {dataset.name}")


if __name__ == "__main__":
    main()
