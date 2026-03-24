import pandas as pd
import psycopg2
from psycopg2 import sql, Error
import json
import sys
import os
import logging
from typing import Dict, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/csv_uploader.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CSVUploader:
    """
    Efficiently uploads large CSV files to PostgreSQL database.
    Handles chunk processing for memory optimization and bulk inserts for speed.
    """
    
    def __init__(self, 
                 host: str = 'localhost',
                 port: int = 5432,
                 database: str = 'survey_db',
                 user: str = 'postgres',
                 password: str = '1234',
                 chunksize: int = 5000):
        """
        Initialize the CSVUploader with database credentials.
        
        Args:
            host: PostgreSQL host address
            port: PostgreSQL port number
            database: Database name
            user: PostgreSQL user
            password: PostgreSQL password
            chunksize: Number of rows to process at a time (default: 5000)
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.chunksize = chunksize
        self.connection = None
        self.total_rows_inserted = 0
        self.total_rows_failed = 0
        self.failed_rows = []
    
    def connect(self) -> bool:
        """
        Establish connection to PostgreSQL database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"✓ Connected to PostgreSQL database: {self.database}")
            return True
        except Error as e:
            logger.error(f"✗ Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("✓ Database connection closed")
    
    def create_table_if_not_exists(self) -> bool:
        """
        Create survey_data table if it doesn't exist.
        
        Returns:
            bool: True if successful, False otherwise
        """
        cursor = None
        try:
            cursor = self.connection.cursor()
            
            # SQL to create table if it doesn't exist
            create_table_query = """
                CREATE TABLE IF NOT EXISTS survey_data (
                    id SERIAL PRIMARY KEY,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            
            cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("✓ Table 'survey_data' is ready")
            return True
        
        except Error as e:
            logger.error(f"✗ Error creating table: {e}")
            return False
        
        finally:
            if cursor:
                cursor.close()
    
    def row_to_json(self, row: pd.Series) -> str:
        """
        Convert a pandas Series (CSV row) to JSON string.
        Handles NaN values and type conversions.
        
        Args:
            row: pandas Series object representing a CSV row
        
        Returns:
            str: JSON string representation of the row
        """
        try:
            # Convert Series to dictionary, replacing NaN with None
            row_dict = row.where(pd.notna(row), None).to_dict()
            
            # Convert to JSON string
            json_str = json.dumps(row_dict, default=str)
            return json_str
        
        except Exception as e:
            logger.warning(f"✗ Error converting row to JSON: {e}")
            return None
    
    def bulk_insert_chunk(self, chunk: pd.DataFrame) -> Tuple[int, int]:
        """
        Insert a chunk of data using bulk insert (executemany).
        Optimized for performance with parameterized queries.
        
        Args:
            chunk: pandas DataFrame containing rows to insert
        
        Returns:
            Tuple: (rows_inserted, rows_failed)
        """
        cursor = None
        rows_inserted = 0
        rows_failed = 0
        
        try:
            cursor = self.connection.cursor()
            
            # Prepare data for bulk insert
            data_to_insert = []
            
            for idx, row in chunk.iterrows():
                json_data = self.row_to_json(row)
                
                if json_data:
                    data_to_insert.append((json_data,))
                else:
                    rows_failed += 1
                    self.failed_rows.append({'row_index': idx, 'reason': 'JSON conversion failed'})
            
            # Bulk insert using executemany with parameterized query
            if data_to_insert:
                insert_query = """
                    INSERT INTO survey_data (data)
                    VALUES (%s)
                """
                
                cursor.executemany(insert_query, data_to_insert)
                self.connection.commit()
                
                rows_inserted = len(data_to_insert)
                logger.info(f"  ✓ Inserted {rows_inserted} rows (batch)")
            
            return rows_inserted, rows_failed
        
        except Error as e:
            logger.error(f"  ✗ Bulk insert error: {e}")
            self.connection.rollback()
            return 0, len(chunk)
        
        finally:
            if cursor:
                cursor.close()
    
    def upload_csv(self, file_path: str) -> bool:
        """
        Main method to upload CSV file to PostgreSQL.
        Processes file in chunks for memory efficiency.
        
        Args:
            file_path: Path to CSV file to upload
        
        Returns:
            bool: True if upload completed, False if failed
        """
        try:
            # Verify file exists using standard Python file handling
            if not os.path.exists(file_path):
                logger.error(f"✗ File not found: {file_path}")
                return False
            
            file_size_bytes = os.path.getsize(file_path)
            file_size_mb = file_size_bytes / (1024 * 1024)
            logger.info(f"Starting CSV upload from: {file_path} ({file_size_mb:.2f} MB)")
            
            # Connect to database
            if not self.connect():
                return False
            
            # Create table if needed
            if not self.create_table_if_not_exists():
                return False
            
            # Start timer
            start_time = datetime.now()
            logger.info(f"Starting upload with chunksize={self.chunksize}")
            
            # Read and process CSV in chunks
            chunk_number = 0
            for chunk in pd.read_csv(file_path, chunksize=self.chunksize):
                chunk_number += 1
                
                # Process this chunk
                rows_inserted, rows_failed = self.bulk_insert_chunk(chunk)
                
                # Update counters
                self.total_rows_inserted += rows_inserted
                self.total_rows_failed += rows_failed
                
                # Progress report
                logger.info(
                    f"Chunk {chunk_number}: "
                    f"Inserted {rows_inserted} rows | "
                    f"Failed {rows_failed} rows | "
                    f"Total: {self.total_rows_inserted} inserted"
                )
            
            # Calculate elapsed time
            elapsed_time = datetime.now() - start_time
            
            # Final summary
            logger.info("=" * 60)
            logger.info("UPLOAD SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Total rows inserted: {self.total_rows_inserted}")
            logger.info(f"Total rows failed: {self.total_rows_failed}")
            logger.info(f"Time elapsed: {elapsed_time}")
            logger.info("=" * 60)
            
            return True
        
        except Exception as e:
            logger.error(f"✗ Unexpected error during upload: {e}")
            return False
        
        finally:
            self.disconnect()
    
    def get_summary(self) -> Dict:
        """
        Get upload summary statistics.
        
        Returns:
            dict: Summary statistics
        """
        return {
            'total_inserted': self.total_rows_inserted,
            'total_failed': self.total_rows_failed,
            'failed_rows': self.failed_rows
        }


def main():
    """
    Example usage of CSVUploader.
    """
    # Configuration
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_NAME = 'survey_db'
    DB_USER = 'postgres'
    DB_PASSWORD = '1234'
    CSV_FILE_PATH = '/path/to/your/large_dataset.csv'  # UPDATE THIS
    CHUNK_SIZE = 5000  # Adjust based on your memory available
    
    # Create uploader instance
    uploader = CSVUploader(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        chunksize=CHUNK_SIZE
    )
    
    # Upload CSV file
    success = uploader.upload_csv(CSV_FILE_PATH)
    
    # Get summary
    summary = uploader.get_summary()
    print("\nFinal Summary:")
    print(f"Rows Inserted: {summary['total_inserted']}")
    print(f"Rows Failed: {summary['total_failed']}")
    
    if summary['failed_rows']:
        print(f"\nFailed rows (first 5):")
        for failed_row in summary['failed_rows'][:5]:
            print(f"  - {failed_row}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
