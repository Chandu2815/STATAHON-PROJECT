"""
Quick usage examples for CSVUploader

This script demonstrates various ways to use the csv_uploader module.
"""

from csv_uploader import CSVUploader
import os


# Example 1: Basic usage with default settings
def example_basic():
    """Upload CSV with default database credentials."""
    uploader = CSVUploader()
    uploader.upload_csv('data/survey_data.csv')
    print(uploader.get_summary())


# Example 2: Custom database credentials and chunk size
def example_custom_settings():
    """Upload CSV with custom database and chunk settings."""
    uploader = CSVUploader(
        host='localhost',
        port=5432,
        database='survey_db',
        user='postgres',
        password='1234',
        chunksize=10000  # Increase chunk size for faster insert (if memory allows)
    )
    
    success = uploader.upload_csv('data/household_data.csv')
    
    if success:
        summary = uploader.get_summary()
        print(f"Successfully inserted {summary['total_inserted']} rows")
        print(f"Failed rows: {summary['total_failed']}")


# Example 3: Multiple CSV files
def example_multiple_files(csv_directory: str):
    """Upload multiple CSV files from a directory."""
    uploader = CSVUploader(
        database='survey_db',
        user='postgres',
        password='1234',
        chunksize=5000
    )
    
    total_rows = 0
    
    # Get all CSV files in directory
    csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]
    
    print(f"Found {len(csv_files)} CSV files to upload")
    
    for csv_file in csv_files:
        file_path = os.path.join(csv_directory, csv_file)
        print(f"\nUploading: {csv_file}")
        
        uploader.upload_csv(file_path)
        summary = uploader.get_summary()
        total_rows += summary['total_inserted']
    
    print(f"\n✓ All files uploaded! Total rows inserted: {total_rows}")


# Example 4: Large file with increased chunk size
def example_large_file_optimized():
    """
    Upload very large file (100GB+) with optimized chunk size.
    Larger chunks = faster insert but more memory usage.
    """
    uploader = CSVUploader(
        database='survey_db',
        user='postgres',
        password='1234',
        chunksize=50000  # Large chunk for faster processing
    )
    
    uploader.upload_csv('data/large_dataset_100gb.csv')


# Example 5: With error handling
def example_with_error_handling():
    """Upload CSV with comprehensive error handling."""
    try:
        uploader = CSVUploader(
            host='localhost',
            port=5432,
            database='survey_db',
            user='postgres',
            password='1234',
            chunksize=5000
        )
        
        csv_file = 'data/survey_data.csv'
        
        # Check if file exists
        if not os.path.exists(csv_file):
            print(f"Error: File '{csv_file}' not found")
            return False
        
        # Upload
        success = uploader.upload_csv(csv_file)
        
        if success:
            summary = uploader.get_summary()
            print(f"✓ Upload completed successfully!")
            print(f"  Inserted: {summary['total_inserted']} rows")
            print(f"  Failed: {summary['total_failed']} rows")
            
            if summary['failed_rows']:
                print("\nFailed row details (first 10):")
                for idx, failed_row in enumerate(summary['failed_rows'][:10], 1):
                    print(f"  {idx}. {failed_row}")
        else:
            print("✗ Upload failed")
            return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Choose which example to run
    print("CSV Uploader - Usage Examples")
    print("=" * 50)
    print("1. Basic usage")
    print("2. Custom settings")
    print("3. Multiple files")
    print("4. Large file (optimized)")
    print("5. With error handling")
    print("=" * 50)
    
    # Uncomment the example you want to run:
    # example_basic()
    # example_custom_settings()
    # example_multiple_files('data/')
    # example_large_file_optimized()
    example_with_error_handling()
