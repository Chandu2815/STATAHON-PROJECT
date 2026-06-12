"""
CSV Data Loader for Survey Data Insert
Loads survey data from CSV files and inserts via the FastAPI endpoint
"""

import pandas as pd
import requests
import logging
from typing import List, Dict, Optional
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SurveyDataCSVLoader:
    """Load and insert survey data from CSV files"""
    
    def __init__(
        self,
        api_url: str = "http://localhost:8002/survey-data/insert",
        batch_size: int = 1000,
        timeout: int = 30
    ):
        """
        Initialize loader
        
        Args:
            api_url: FastAPI insert endpoint URL
            batch_size: Records per request (max 10000)
            timeout: Request timeout in seconds
        """
        self.api_url = api_url
        self.batch_size = min(batch_size, 10000)
        self.timeout = timeout
        self.stats = {
            "total_inserted": 0,
            "total_skipped": 0,
            "total_errors": 0,
            "batches_processed": 0
        }
    
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """
        Load CSV file with survey data
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            pandas DataFrame with survey data
        """
        logger.info(f"Loading CSV from: {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} rows from CSV")
            
            # Display column info
            logger.info(f"Columns: {df.columns.tolist()}")
            logger.info(f"Data types:\n{df.dtypes}")
            
            return df
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise
    
    def transform_csv_data(
        self,
        df: pd.DataFrame,
        mapping: Optional[Dict[str, str]] = None
    ) -> List[Dict]:
        """
        Transform CSV data to survey record format
        
        Args:
            df: DataFrame from CSV
            mapping: Optional column mapping {csv_col: schema_field}
                    If None, uses default mapping
                    
        Returns:
            List of dicts matching SurveyDataRecord schema
        """
        
        # Default column mapping for common CSV formats
        default_mapping = {
            'dataset_name': 'dataset_name',
            'category': 'category',
            'year': 'year',
            'indicator_name': 'indicator_name',
            'indicator': 'indicator_name',
            'value': 'value',
            'amount': 'value',
            'quantity': 'value',
            'state': 'state',
            'district': 'district'
        }
        
        mapping = mapping or default_mapping
        records = []
        
        for idx, row in df.iterrows():
            try:
                # Extract and transform values
                record = {}
                
                # Required fields
                for csv_col, schema_field in mapping.items():
                    if csv_col in df.columns and schema_field in [
                        'dataset_name', 'category', 'year', 
                        'indicator_name', 'value', 'state', 'district'
                    ]:
                        value = row.get(csv_col)
                        
                        # Handle None/NaN values
                        if pd.isna(value):
                            if schema_field in ['district']:
                                record[schema_field] = None
                            else:
                                logger.warning(f"Row {idx}: Missing required field {schema_field}")
                                continue
                        else:
                            # Type conversion
                            if schema_field == 'year':
                                record[schema_field] = int(value)
                            elif schema_field == 'value':
                                record[schema_field] = float(value)
                            else:
                                record[schema_field] = str(value).strip()
                
                # Validate record has all required fields
                required_fields = [
                    'dataset_name', 'category', 'year',
                    'indicator_name', 'value', 'state'
                ]
                
                if all(field in record for field in required_fields):
                    records.append(record)
                else:
                    missing = [f for f in required_fields if f not in record]
                    logger.warning(f"Row {idx}: Missing fields {missing}")
                    
            except Exception as e:
                logger.warning(f"Row {idx}: Error transforming - {str(e)}")
                continue
        
        logger.info(f"Transformed {len(records)} valid records from {len(df)} CSV rows")
        return records
    
    def insert_records_batch(self, records: List[Dict], skip_duplicates: bool = True) -> dict:
        """
        Insert a batch of records via API
        
        Args:
            records: List of survey data records
            skip_duplicates: Whether to skip duplicate entries
            
        Returns:
            Response dict with insert stats
        """
        
        if not records:
            logger.warning("No records to insert")
            return {
                "inserted": 0,
                "skipped": 0,
                "errors": 0
            }
        
        try:
            logger.info(f"Inserting batch of {len(records)} records...")
            
            response = requests.post(
                self.api_url,
                json={
                    "records": records,
                    "skip_duplicates": skip_duplicates
                },
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            result = {
                "inserted": data.get("inserted_count", 0),
                "skipped": data.get("skipped_count", 0),
                "errors": len(data.get("errors", []))
            }
            
            logger.info(
                f"Batch result: {result['inserted']} inserted, "
                f"{result['skipped']} skipped, {result['errors']} errors"
            )
            
            # Update global stats
            self.stats["total_inserted"] += result["inserted"]
            self.stats["total_skipped"] += result["skipped"]
            self.stats["total_errors"] += result["errors"]
            self.stats["batches_processed"] += 1
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
    
    def load_and_insert(
        self,
        filepath: str,
        skip_duplicates: bool = True,
        mapping: Optional[Dict[str, str]] = None,
        start_row: Optional[int] = None,
        end_row: Optional[int] = None
    ) -> dict:
        """
        Load CSV and insert all records in batches
        
        Args:
            filepath: Path to CSV file
            skip_duplicates: Skip duplicate entries
            mapping: Optional column mapping
            start_row: Start row index (for resuming)
            end_row: End row index
            
        Returns:
            Overall statistics
        """
        
        logger.info("=== Starting CSV Load & Insert Process ===")
        
        try:
            # Load CSV
            df = self.load_csv(filepath)
            
            # Apply row limits if specified
            if start_row is not None or end_row is not None:
                df = df.iloc[start_row:end_row]
                logger.info(f"Processing rows {start_row} to {end_row}")
            
            # Transform data
            records = self.transform_csv_data(df, mapping)
            
            if not records:
                logger.error("No valid records to insert")
                return self.stats
            
            # Insert in batches
            total_batches = (len(records) + self.batch_size - 1) // self.batch_size
            logger.info(f"Processing {len(records)} records in {total_batches} batches...")
            
            for i in range(0, len(records), self.batch_size):
                batch = records[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                
                logger.info(f"\nBatch {batch_num}/{total_batches}")
                self.insert_records_batch(batch, skip_duplicates)
                
                # Add delay between batches to avoid overwhelming the server
                if batch_num < total_batches:
                    time.sleep(0.5)
            
            logger.info("\n=== Load & Insert Complete ===")
            logger.info(f"Total Inserted: {self.stats['total_inserted']}")
            logger.info(f"Total Skipped: {self.stats['total_skipped']}")
            logger.info(f"Total Errors: {self.stats['total_errors']}")
            logger.info(f"Batches Processed: {self.stats['batches_processed']}")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Load & insert failed: {str(e)}")
            raise


# ============================================================================
# Command Line Interface
# ============================================================================

if __name__ == "__main__":
    import sys
    
    """
    Usage:
        python csv_loader.py <csv_file> [--api-url URL] [--batch-size SIZE]
        
    Example:
        python csv_loader.py DataSet.csv
        python csv_loader.py data/survey.csv --batch-size 2000
        python csv_loader.py data/survey.csv --api-url http://localhost:8002/survey-data/insert
    """
    
    # Parse arguments
    filepath = sys.argv[1] if len(sys.argv) > 1 else "DataSet.csv"
    
    api_url = "http://localhost:8002/survey-data/insert"
    batch_size = 1000
    
    for i, arg in enumerate(sys.argv[2:]):
        if arg == "--api-url" and i + 3 < len(sys.argv):
            api_url = sys.argv[i + 3]
        elif arg == "--batch-size" and i + 3 < len(sys.argv):
            batch_size = int(sys.argv[i + 3])
    
    # Initialize loader
    loader = SurveyDataCSVLoader(api_url=api_url, batch_size=batch_size)
    
    # Load and insert
    try:
        stats = loader.load_and_insert(filepath)
        sys.exit(0 if stats["total_inserted"] > 0 else 1)
    except Exception as e:
        logger.error(f"Failed: {str(e)}")
        sys.exit(1)
