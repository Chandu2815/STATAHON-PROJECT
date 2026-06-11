"""
Robust CSV to PostgreSQL Uploader
Handles large datasets (100GB+) with chunk processing, encoding fallback, and advanced error handling.
"""

import pandas as pd
import psycopg2
from psycopg2 import sql, Error
import json
import sys
import logging
from typing import Dict, Tuple, List, Optional
from datetime import datetime
import os

# Configure logging with both file and console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler('csv_uploader.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RobustCSVUploader:
    """
    Production-grade CSV to PostgreSQL uploader with advanced features:
    - Chunk-based processing for memory efficiency
    - Encoding detection and fallback (utf-8 → latin1)
    - Null value handling
    - Bulk insert optimization
    - Comprehensive error tracking and recovery
    """
    
    def __init__(self,
                 host: str = '187.127.138.4',
                 port: int = 5432,
                 database: str = 'statahon_db',
                 user: str = 'postgres',
                 password: str = 'NewPassword123',
                 chunksize: int = 5000):
        """
        Initialize the uploader with database credentials.
        
        Args:
            host: PostgreSQL host (default: localhost)
            port: PostgreSQL port (default: 5432)
            database: Database name (default: survey_db)
            user: PostgreSQL user (default: postgres)
            password: PostgreSQL password (default: 1234)
            chunksize: Rows per batch (default: 5000)
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.chunksize = chunksize
        
        # Statistics tracking
        self.connection = None
        self.total_rows_inserted = 0
        self.total_rows_skipped = 0
        self.total_chunks_processed = 0
        self.failed_rows_log: List[Dict] = []
        self.start_time = None
        self.end_time = None
    
    def connect(self) -> bool:
        """
        Establish PostgreSQL connection.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                connect_timeout=10
            )
            logger.info(f"✓ Connected to {self.database}@{self.host}:{self.port}")
            return True
        except Error as e:
            logger.error(f"✗ Connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Close database connection safely."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("✓ Database connection closed")
            except Exception as e:
                logger.warning(f"Warning closing connection: {e}")
    
    def create_table_if_not_exists(self) -> bool:
        """
        Create survey_data table with proper schema if it doesn't exist.
        
        Returns:
            bool: True if successful, False otherwise
        """
        cursor = None
        try:
            cursor = self.connection.cursor()
            
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS survey_data (
                    id SERIAL PRIMARY KEY,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_survey_data_created_at 
                ON survey_data(created_at DESC);
            """
            
            cursor.execute(create_table_sql)
            self.connection.commit()
            logger.info("✓ Table 'survey_data' ready (with indexes)")
            return True
        
        except Error as e:
            logger.error(f"✗ Table creation failed: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        
        finally:
            if cursor:
                cursor.close()
    
    def detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding, fallback from utf-8 to latin1.
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            str: Detected encoding ('utf-8' or 'latin1')
        """
        try:
            # Try UTF-8 first (most common)
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(10000)
            logger.info("✓ Detected encoding: UTF-8")
            return 'utf-8'
        except UnicodeDecodeError:
            logger.warning("⚠ UTF-8 decoding failed, falling back to latin1")
            return 'latin1'
        except Exception as e:
            logger.warning(f"⚠ Encoding detection error: {e}, using UTF-8")
            return 'utf-8'
    
    def row_to_json(self, row: pd.Series, row_index: int) -> Optional[str]:
        """
        Convert pandas Series to JSON string with null value handling.
        
        Args:
            row: pandas Series (CSV row)
            row_index: Row index for error tracking
        
        Returns:
            str: JSON string or None if conversion fails
        """
        try:
            # Convert Series to dictionary
            row_dict = row.to_dict()
            
            # Drop null/NaN values
            row_dict = {k: v for k, v in row_dict.items() 
                       if pd.notna(v) and v != ''}
            
            # Convert to JSON string
            json_str = json.dumps(row_dict, default=str, ensure_ascii=False)
            return json_str
        
        except Exception as e:
            self.failed_rows_log.append({
                'row_index': row_index,
                'error': f'JSON conversion: {str(e)}'
            })
            return None
    
    def validate_row(self, row: pd.Series, row_index: int) -> bool:
        """
        Validate row data before insertion.
        
        Args:
            row: pandas Series to validate
            row_index: Row index for error tracking
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check if row has at least some non-null values
            if row.isna().all():
                self.failed_rows_log.append({
                    'row_index': row_index,
                    'error': 'All columns are null'
                })
                return False
            
            return True
        
        except Exception as e:
            logger.debug(f"Validation error for row {row_index}: {e}")
            return False
    
    def bulk_insert_chunk(self, chunk: pd.DataFrame, chunk_num: int) -> Tuple[int, int]:
        """
        Bulk insert a chunk of data using executemany().
        
        Args:
            chunk: pandas DataFrame containing rows to insert
            chunk_num: Chunk number for logging
        
        Returns:
            Tuple: (rows_inserted, rows_skipped)
        """
        cursor = None
        rows_inserted = 0
        rows_skipped = 0
        
        try:
            cursor = self.connection.cursor()
            data_to_insert = []
            
            # Process each row in chunk
            for idx, (row_index, row) in enumerate(chunk.iterrows()):
                # Validate row
                if not self.validate_row(row, row_index):
                    rows_skipped += 1
                    continue
                
                # Convert to JSON
                json_data = self.row_to_json(row, row_index)
                
                if json_data:
                    data_to_insert.append((json_data,))
                else:
                    rows_skipped += 1
            
            # Bulk insert using executemany
            if data_to_insert:
                insert_sql = "INSERT INTO survey_data (data) VALUES (%s)"
                cursor.executemany(insert_sql, data_to_insert)
                self.connection.commit()
                rows_inserted = len(data_to_insert)
                
                logger.info(
                    f"  Chunk {chunk_num}: "
                    f"Inserted {rows_inserted} | "
                    f"Skipped {rows_skipped} | "
                    f"Total: {self.total_rows_inserted + rows_inserted}"
                )
            else:
                logger.warning(f"  Chunk {chunk_num}: No valid rows to insert")
            
            return rows_inserted, rows_skipped
        
        except Error as e:
            logger.error(f"  ✗ Chunk {chunk_num} insert failed: {e}")
            if self.connection:
                self.connection.rollback()
            return 0, len(chunk)
        
        finally:
            if cursor:
                cursor.close()
    
    def upload_csv(self, file_path: str) -> bool:
        """
        Main method: Upload CSV file to PostgreSQL with all safety features.
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Validation
        if not os.path.exists(file_path):
            logger.error(f"✗ File not found: {file_path}")
            return False
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        logger.info(f"Starting upload: {file_path} ({file_size_mb:.2f} MB)")
        
        # Initialize
        self.start_time = datetime.now()
        self.total_rows_inserted = 0
        self.total_rows_skipped = 0
        self.total_chunks_processed = 0
        self.failed_rows_log = []
        
        try:
            # Connect to database
            if not self.connect():
                return False
            
            # Create table if needed
            if not self.create_table_if_not_exists():
                return False
            
            # Detect encoding
            encoding = self.detect_encoding(file_path)
            
            logger.info(f"Processing CSV with chunksize={self.chunksize}")
            
            # Read and process CSV in chunks
            chunk_num = 0
            for chunk in pd.read_csv(
                file_path,
                chunksize=self.chunksize,
                encoding=encoding,
                low_memory=False,  # Ensures consistent dtype inference
                on_bad_lines='skip'  # Skip malformed rows
            ):
                chunk_num += 1
                self.total_chunks_processed = chunk_num
                
                # Insert chunk
                rows_inserted, rows_skipped = self.bulk_insert_chunk(chunk, chunk_num)
                
                # Update counters
                self.total_rows_inserted += rows_inserted
                self.total_rows_skipped += rows_skipped
            
            # Calculate elapsed time
            self.end_time = datetime.now()
            elapsed = self.end_time - self.start_time
            
            # Print summary
            self._print_summary(elapsed)
            return True
        
        except Exception as e:
            logger.error(f"✗ Unexpected error: {e}")
            return False
        
        finally:
            self.disconnect()
    
    def _print_summary(self, elapsed):
        """Print detailed upload summary."""
        logger.info("=" * 70)
        logger.info("UPLOAD SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Chunks processed: {self.total_chunks_processed}")
        logger.info(f"Rows inserted: {self.total_rows_inserted:,}")
        logger.info(f"Rows skipped: {self.total_rows_skipped:,}")
        
        if self.total_rows_inserted > 0:
            rate = self.total_rows_inserted / elapsed.total_seconds()
            logger.info(f"Insert rate: {rate:,.0f} rows/second")
        
        logger.info(f"Time elapsed: {elapsed}")
        
        if self.failed_rows_log:
            logger.info(f"\n⚠ Failed rows (first 5):")
            for failed in self.failed_rows_log[:5]:
                logger.info(f"  - Row {failed['row_index']}: {failed['error']}")
        
        logger.info("=" * 70 + "\n")
    
    def get_statistics(self) -> Dict:
        """
        Get upload statistics.
        
        Returns:
            dict: Statistics including counts, rate, and failed rows
        """
        if self.start_time and self.end_time:
            elapsed = (self.end_time - self.start_time).total_seconds()
            rate = self.total_rows_inserted / elapsed if elapsed > 0 else 0
        else:
            rate = 0
        
        return {
            'total_inserted': self.total_rows_inserted,
            'total_skipped': self.total_rows_skipped,
            'chunks_processed': self.total_chunks_processed,
            'rows_per_second': rate,
            'failed_rows': self.failed_rows_log
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """Example: Upload CSV file."""
    
    # Configuration
    DB_HOST = '187.127.138.4'
    DB_PORT = 5432
    DB_NAME = 'statahon_db'
    DB_USER = 'postgres'
    DB_PASSWORD = 'NewPassword123'
    CSV_FILE = 'data/survey_data.csv'  # UPDATE THIS PATH
    CHUNK_SIZE = 5000
    
    # Create uploader
    uploader = RobustCSVUploader(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        chunksize=CHUNK_SIZE
    )
    
    # Upload
    logger.info("=" * 70)
    logger.info("CSV TO POSTGRESQL UPLOADER")
    logger.info("=" * 70)
    
    success = uploader.upload_csv(CSV_FILE)
    
    # Get statistics
    stats = uploader.get_statistics()
    
    if success:
        logger.info("✓ Upload completed successfully!")
    else:
        logger.error("✗ Upload failed - check logs above")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
