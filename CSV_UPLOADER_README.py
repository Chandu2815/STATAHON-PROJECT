"""
CSV to PostgreSQL Uploader - Quick Reference Guide

This module provides an efficient way to upload large CSV files to PostgreSQL
using pandas chunking and bulk inserts.
"""

# ============================================================================
# QUICK START
# ============================================================================

from csv_uploader import CSVUploader

# Method 1: Default settings (localhost, postgres user, survey_db)
uploader = CSVUploader()
uploader.upload_csv('data/survey_data.csv')


# Method 2: Custom database credentials
uploader = CSVUploader(
    host='127.0.0.1',
    port=5432,
    database='survey_db',
    user='postgres',
    password='1234',
    chunksize=5000  # Number of rows per batch
)
success = uploader.upload_csv('data/survey_data.csv')

# Get upload summary
summary = uploader.get_summary()
print(f"Inserted: {summary['total_inserted']} rows")
print(f"Failed: {summary['total_failed']} rows")


# ============================================================================
# KEY FEATURES
# ============================================================================

"""
1. CHUNK PROCESSING
   - Processes CSV in chunks to minimize memory usage
   - Default chunksize=5000 (adjust based on available RAM)
   - For 100GB+ files, no need to load entire file in memory

2. BULK INSERT
   - Uses executemany() for batch inserts (faster than row-by-row)
   - Parameterized queries prevent SQL injection
   - Commits after each chunk for transaction management

3. JSON CONVERSION
   - Automatically converts CSV rows to JSON format
   - Handles NaN values, converts to None/null
   - Inserts as JSONB into PostgreSQL (better querying)

4. ERROR HANDLING
   - Gracefully handles bad rows (skips them, logs errors)
   - Creates table if not exists
   - Logs all operations to file + console

5. PROGRESS TRACKING
   - Reports progress after each batch
   - Shows total rows inserted so far
   - Provides final summary with elapsed time
"""


# ============================================================================
# CONFIGURATION EXAMPLES
# ============================================================================

# Small files (< 1GB)
uploader = CSVUploader(chunksize=5000)  # Default

# Medium files (1-10GB)
uploader = CSVUploader(chunksize=10000)  # Increase chunk size

# Large files (10-100GB)
uploader = CSVUploader(chunksize=50000)  # Much larger chunks

# Very large files (100GB+)
uploader = CSVUploader(chunksize=100000)  # Very large chunks (use if RAM allows)


# ============================================================================
# DATABASE SETUP (First Time Only)
# ============================================================================

"""
Ensure PostgreSQL is running and database exists:

1. Login to PostgreSQL:
   psql -U postgres -h 127.0.0.1

2. Create database (if not exists):
   CREATE DATABASE survey_db;

3. The uploader will automatically create the 'survey_data' table
   with columns: id (SERIAL PRIMARY KEY), data (JSONB), created_at (TIMESTAMP)
"""


# ============================================================================
# INSTALLATION
# ============================================================================

"""
pip install pandas psycopg2-binary
"""


# ============================================================================
# LOGGING
# ============================================================================

"""
All operations are logged to:
- File: /tmp/csv_uploader.log
- Console: stdout

To check progress while running:
tail -f /tmp/csv_uploader.log
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Problem: "Failed to connect to database"
Solution: Ensure PostgreSQL is running and credentials are correct

Problem: "Out of memory"
Solution: Reduce chunksize (e.g., 5000 instead of 50000)

Problem: "Many failed rows"
Solution: Check CSV file format, encoding (should be UTF-8)
         Some rows might have invalid data that can't be JSONified

Problem: "Slow insert speed"
Solution: Increase chunksize if memory allows
          Use SSD storage for PostgreSQL data directory
          Disable indexes during bulk insert (for very large files)
"""


# ============================================================================
# PERFORMANCE TIPS
# ============================================================================

"""
1. Chunk Size Selection:
   - Memory = ~4GB * chunksize / 100000
   - E.g., chunksize=5000 uses ~200MB per chunk
   - Start with 5000, increase if you have spare RAM

2. Database Optimization:
   - Ensure PostgreSQL work_mem is sufficient:
     SET work_mem = '256MB';

3. CSV File Format:
   - Ensure CSV is UTF-8 encoded
   - Use consistent column names
   - Minimize special characters if possible

4. Parallel Processing:
   - For multiple CSV files, upload sequentially
   - Or use separate uploader instances in different processes
"""


# ============================================================================
# EXAMPLE: STEP BY STEP
# ============================================================================

"""
from csv_uploader import CSVUploader

# 1. Create uploader instance
uploader = CSVUploader(
    host='127.0.0.1',
    port=5432,
    database='survey_db',
    user='postgres',
    password='1234',
    chunksize=5000
)

# 2. Upload CSV file
success = uploader.upload_csv('data/large_survey.csv')

# 3. Check results
if success:
    summary = uploader.get_summary()
    print(f"Successfully inserted {summary['total_inserted']} rows")
else:
    print("Upload failed - check logs")

# Output example:
# 2024-03-24 10:15:30,123 - INFO - Connected to PostgreSQL database: survey_db
# 2024-03-24 10:15:31,456 - INFO - Table 'survey_data' is ready
# 2024-03-24 10:15:33,789 - INFO - Starting upload with chunksize=5000
# 2024-03-24 10:15:35,012 - INFO - Chunk 1: Inserted 5000 rows | Failed 0 rows | Total: 5000 inserted
# 2024-03-24 10:15:37,345 - INFO - Chunk 2: Inserted 5000 rows | Failed 0 rows | Total: 10000 inserted
# ...
"""
