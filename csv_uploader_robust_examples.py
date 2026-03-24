"""
Usage Guide: RobustCSVUploader
Complete examples for various scenarios
"""

from csv_uploader_robust import RobustCSVUploader
import logging
import os


# ============================================================================
# EXAMPLE 1: Basic Usage
# ============================================================================

def example_basic():
    """Simplest way to upload a CSV file."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 70)
    
    uploader = RobustCSVUploader()  # Uses defaults
    success = uploader.upload_csv('data/survey_data.csv')
    
    if success:
        stats = uploader.get_statistics()
        print(f"\nInserted: {stats['total_inserted']:,} rows")
        print(f"Skipped: {stats['total_skipped']:,} rows")


# ============================================================================
# EXAMPLE 2: Custom Configuration
# ============================================================================

def example_custom_config():
    """Upload with custom database credentials and chunk size."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Custom Configuration")
    print("=" * 70)
    
    uploader = RobustCSVUploader(
        host='127.0.0.1',
        port=5432,
        database='survey_db',
        user='postgres',
        password='1234',
        chunksize=10000  # Larger chunks for faster insert
    )
    
    success = uploader.upload_csv('data/large_survey.csv')
    
    if success:
        stats = uploader.get_statistics()
        print(f"\nRows/second: {stats['rows_per_second']:.0f}")


# ============================================================================
# EXAMPLE 3: Large File Optimization
# ============================================================================

def example_large_file():
    """Optimized settings for 100GB+ files."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Large File (100GB+) Optimization")
    print("=" * 70)
    
    uploader = RobustCSVUploader(
        database='survey_db',
        user='postgres',
        password='1234',
        chunksize=50000  # Much larger chunks for speed
    )
    
    # For files this large, you want:
    # - More RAM available (16GB+)
    # - SSD storage for PostgreSQL
    # - Potentially parallel loading on multiple processes
    
    success = uploader.upload_csv('data/huge_dataset_100gb.csv')
    
    if success:
        stats = uploader.get_statistics()
        print(f"\nTotal rows: {stats['total_inserted']:,}")


# ============================================================================
# EXAMPLE 4: Multiple Files
# ============================================================================

def example_multiple_files(directory: str):
    """Upload all CSV files from a directory."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Multiple Files")
    print("=" * 70)
    
    uploader = RobustCSVUploader(chunksize=5000)
    
    total_inserted = 0
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    
    print(f"Found {len(csv_files)} CSV files")
    
    for i, csv_file in enumerate(csv_files, 1):
        file_path = os.path.join(directory, csv_file)
        print(f"\n[{i}/{len(csv_files)}] Uploading: {csv_file}")
        
        success = uploader.upload_csv(file_path)
        
        if success:
            stats = uploader.get_statistics()
            total_inserted += stats['total_inserted']
    
    print(f"\n✓ All files uploaded! Total: {total_inserted:,} rows")


# ============================================================================
# EXAMPLE 5: Error Handling & Recovery
# ============================================================================

def example_with_error_handling():
    """Upload with comprehensive error handling."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Error Handling & Recovery")
    print("=" * 70)
    
    try:
        # Configuration
        csv_file = 'data/survey_data.csv'
        
        # Validate file exists
        if not os.path.exists(csv_file):
            print(f"✗ File not found: {csv_file}")
            return False
        
        # Create uploader
        uploader = RobustCSVUploader(
            host='localhost',
            port=5432,
            database='survey_db',
            user='postgres',
            password='1234',
            chunksize=5000
        )
        
        # Upload with error handling
        print(f"Uploading: {csv_file}")
        success = uploader.upload_csv(csv_file)
        
        if success:
            stats = uploader.get_statistics()
            
            print("\n✓ UPLOAD SUCCESSFUL")
            print(f"  Inserted: {stats['total_inserted']:,} rows")
            print(f"  Skipped: {stats['total_skipped']:,} rows")
            print(f"  Rate: {stats['rows_per_second']:.0f} rows/second")
            
            # Show failed rows if any
            if stats['failed_rows']:
                print(f"\n⚠ Failed rows: {len(stats['failed_rows'])}")
                for failed in stats['failed_rows'][:3]:
                    print(f"  - Row {failed['row_index']}: {failed['error']}")
        else:
            print("\n✗ UPLOAD FAILED - Check logs")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True


# ============================================================================
# EXAMPLE 6: Performance Tuning
# ============================================================================

def example_performance_tuning():
    """Tips for optimizing upload performance."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Performance Tuning")
    print("=" * 70)
    
    print("""
    MEMORY OPTIMIZATION:
    --------------------
    Chunk Size  │ Memory Used (approx)  │ Use Case
    ────────────├──────────────────────┼─────────────────────
    5,000       │ ~50 MB               │ Low RAM, stable inserts
    10,000      │ ~100 MB              │ Normal case (default)
    50,000      │ ~500 MB              │ High RAM available
    100,000     │ ~1 GB                │ Very large RAM (16GB+)
    
    
    DATABASE OPTIMIZATION:
    ----------------------
    1. Use SSD storage for PostgreSQL data directory
    2. Increase PostgreSQL work_mem before bulk insert:
       
       ALTER SYSTEM SET work_mem = '256MB';
       SELECT pg_reload_conf();
    
    3. Temporarily increase max_wal_size during bulk loads:
       
       ALTER SYSTEM SET max_wal_size = '2GB';
    
    4. Disable autovacuum during massive inserts:
       
       ALTER TABLE survey_data SET (autovacuum_enabled = false);
    
    
    CSV FILE OPTIMIZATION:
    ----------------------
    1. Pre-clean CSV file (remove invalid rows)
    2. Ensure UTF-8 encoding (not latin1 with mixed encodings)
    3. Use consistent column order
    4. Consider preprocessing to remove null-only rows
    """)
    
    # Example with tuned settings
    print("\nTuned uploader for 100GB+ files:")
    uploader = RobustCSVUploader(
        chunksize=50000  # Large chunks
    )
    print(f"  - Chunk size: 50,000 rows")
    print(f"  - Memory per chunk: ~500 MB")
    print(f"  - Suitable for systems with 16GB+ RAM")


# ============================================================================
# EXAMPLE 7: Progress Monitoring
# ============================================================================

def example_progress_monitoring():
    """Monitor upload progress in real-time."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Real-time Progress Monitoring")
    print("=" * 70)
    
    print("""
    During upload, check progress with:
    
    1. Terminal (tail the log file):
       $ tail -f csv_uploader.log
    
    2. PostgreSQL (in another terminal):
       $ psql -U postgres -d survey_db -c "SELECT COUNT(*) FROM survey_data;"
    
    3. System monitoring:
       $ watch -n 1 'psql -U postgres -d survey_db -c "SELECT COUNT(*) FROM survey_data;"'
    
    
    Expected output during upload:
    
    $ tail -f csv_uploader.log
    2024-03-24 10:15:30 | INFO | Starting upload: data.csv (5234.56 MB)
    2024-03-24 10:15:31 | INFO | ✓ Connected to survey_db@localhost:5432
    2024-03-24 10:15:32 | INFO | ✓ Table 'survey_data' ready (with indexes)
    2024-03-24 10:15:33 | INFO | ✓ Detected encoding: UTF-8
    2024-03-24 10:15:33 | INFO | Processing CSV with chunksize=50000
    2024-03-24 10:15:35 | INFO | Chunk 1: Inserted 50000 | Skipped 0 | Total: 50000
    2024-03-24 10:15:37 | INFO | Chunk 2: Inserted 50000 | Skipped 0 | Total: 100000
    ...
    """)


# ============================================================================
# MAIN: Choose Example
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ROBUST CSV UPLOADER - USAGE EXAMPLES")
    print("=" * 70)
    print("""
    Available examples:
    1. Basic usage
    2. Custom configuration
    3. Large file optimization
    4. Multiple files
    5. Error handling
    6. Performance tuning
    7. Progress monitoring
    """)
    
    # Uncomment the example to run:
    # example_basic()
    # example_custom_config()
    # example_large_file()
    # example_multiple_files('data/')
    example_with_error_handling()
    # example_performance_tuning()
    # example_progress_monitoring()
    
    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70 + "\n")
