"""
Testing & Troubleshooting Guide for RobustCSVUploader
Complete guide for validation and problem-solving
"""

# ============================================================================
# TESTING & VALIDATION
# ============================================================================

"""
STEP 1: VERIFY ENVIRONMENT
===========================

1. Check Python version:
   $ python --version
   # Requirement: Python 3.8+

2. Check installed packages:
   $ pip list | grep -E "pandas|psycopg2|sqlalchemy"
   
   Required packages:
   ✓ pandas >= 1.3.0
   ✓ psycopg2-binary >= 2.9.0

3. Install/upgrade packages:
   $ pip install --upgrade pandas psycopg2-binary


STEP 2: VERIFY POSTGRESQL
==========================

1. Check PostgreSQL is running:
   $ psql -U postgres -d postgres -c "SELECT version();"
   
   Expected: PostgreSQL version information

2. Test connection to survey_db:
   $ psql -U postgres -d survey_db -c "\\dt"
   
   Expected: List of tables (empty if new database)

3. Create database if not exists:
   $ psql -U postgres -c "CREATE DATABASE survey_db;"
   $ psql -U postgres -c "CREATE USER survey_user WITH PASSWORD 'StrongPass@123';"
   $ psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE survey_db TO survey_user;"


STEP 3: TEST CSV FILE FORMAT
=============================

1. Inspect CSV structure:
   $ head -5 data/survey_data.csv
   
   Expected: Headers, followed by data rows

2. Check file encoding:
   $ file data/survey_data.csv
   
   Expected: "UTF-8 Unicode" or "ASCII text"

3. Verify no obvious corruption:
   $ tail -c 100 data/survey_data.csv
   
   Expected: Last few characters, not corrupted

4. Row count:
   $ wc -l data/survey_data.csv
   
   Expected: Number of lines (including header)


STEP 4: TEST DATABASE CONNECTION
=================================

Create test script:

```python
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='survey_db',
        user='postgres',
        password='1234'
    )
    print("✓ Connection successful")
    conn.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

Run test:
   $ python test_connection.py


STEP 5: RUN UPLOADER WITH TEST FILE
====================================

1. Create small test CSV (100 rows):
   $ head -101 data/large_dataset.csv > data/test_small.csv

2. Run uploader:
   $ python csv_uploader_robust.py
   
   (and modify main() to use test_small.csv)

3. Verify rows inserted:
   $ psql -U postgres -d survey_db -c "SELECT COUNT(*) FROM survey_data;"


STEP 6: VALIDATE DATA INTEGRITY
================================

1. Check JSONB data structure:
   $ psql -U postgres -d survey_db -c "SELECT id, data FROM survey_data LIMIT 1;"

2. Check for NULL values in data column:
   $ psql -U postgres -d survey_db -c "SELECT COUNT(*) FROM survey_data WHERE data IS NULL;"
   
   Expected: 0

3. Sample a few rows:
   $ psql -U postgres -d survey_db -c "SELECT jsonb_pretty(data) FROM survey_data LIMIT 2;"
"""


# ============================================================================
# TROUBLESHOOTING GUIDE
# ============================================================================

TROUBLESHOOTING = """

PROBLEM 1: "Failed to connect to database"
===========================================

Symptoms:
  ✗ Connection failed: could not connect to server: Connection refused

Solutions:
  1. Verify PostgreSQL is running:
     $ sudo systemctl status postgresql
     
     If not running, start it:
     $ sudo systemctl start postgresql

  2. Check credentials are correct:
     - host: localhost (or 127.0.0.1)
     - port: 5432 (default)
     - database: survey_db (create if missing)
     - user: postgres

  3. Check firewall isn't blocking:
     $ sudo ufw allow 5432/tcp

  4. Verify database exists:
     $ psql -U postgres -l | grep survey_db


PROBLEM 2: "Database 'survey_db' does not exist"
=================================================

Symptoms:
  ✗ FATAL: database "survey_db" does not exist

Solutions:
  1. Create the database:
     $ psql -U postgres -c "CREATE DATABASE survey_db;"

  2. Verify creation:
     $ psql -U postgres -l | grep survey_db


PROBLEM 3: "UTF-8 codec can't decode..."
========================================

Symptoms:
  ✗ UnicodeDecodeError: 'utf-8' codec can't decode...

Solutions:
  1. Automatic fallback:
     The uploader automatically falls back to latin1 encoding
     Check log: "UTF-8 decoding failed, falling back to latin1"

  2. Manual fix (convert CSV to UTF-8):
     $ iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv

  3. Check actual encoding:
     $ file data/survey_data.csv


PROBLEM 4: "Out of memory" during upload
=========================================

Symptoms:
  ✗ MemoryError or process killed

Solutions:
  1. Reduce chunksize:
     # Instead of 50000, use:
     uploader = RobustCSVUploader(chunksize=5000)

  2. Check available RAM:
     $ free -h
     
     Required: chunksize * 10MB min

  3. Close other applications

  4. For 100GB+ files, consider:
     - Use machine with more RAM (32GB+)
     - Pre-split CSV into smaller parts
     - Process sequentially


PROBLEM 5: "Too many inserts rejected"
======================================

Symptoms:
  ⚠ Many rows marked as "Skipped"

Solutions:
  1. Check CSV for bad rows:
     $ head -20 data/survey_data.csv

  2. Look for:
     - Mismatched column count
     - Missing values
     - Special characters

  3. Pre-clean CSV:
     $ python -m pandas script.py
     
     Example:
     ```python
     import pandas as pd
     df = pd.read_csv('data_dirty.csv', on_bad_lines='skip')
     df.dropna(subset=df.columns[:1], inplace=True)  # Keep rows with key column
     df.to_csv('data_clean.csv', index=False)
     ```


PROBLEM 6: "Process very slow"
==============================

Symptoms:
  - Rows/second < 100
  - Inserts taking hours for millions of rows

Solutions:
  1. Increase chunksize:
     uploader = RobustCSVUploader(chunksize=50000)

  2. Check disk performance:
     $ iostat -x 1
     # Look for high await times

  3. Optimize PostgreSQL (temporarily):
     $ psql -U postgres -d survey_db
     
     survey_db=# ALTER SYSTEM SET checkpoint_timeout = '30min';
     survey_db=# SELECT pg_reload_conf();

  4. Use faster storage (SSD vs HDD)


PROBLEM 7: "Connection timeout after some rows"
===============================================

Symptoms:
  ✗ Inserted 50000 rows, then timeout
  ✗ Server closed the connection unexpectedly

Solutions:
  1. Increase connection timeout:
     uploader = RobustCSVUploader()
     # Already has 10s timeout, add this if needed:
     # Edit csv_uploader_robust.py, line 120:
     # connect_timeout=30  # Increase to 30s

  2. Check PostgreSQL logs:
     $ tail /var/log/postgresql/postgresql.log

  3. Commit more frequently:
     Already done after each chunk

  4. Check network stability:
     $ ping -c 100 localhost


PROBLEM 8: "Duplicate key error after restart"
==============================================

Symptoms:
  ✗ Error: duplicate key value violates unique constraint
  ✗ After restart, some rows re-inserted

Solutions:
  1. The SERIAL ID sequencer needs reset:
     $ psql -U postgres -d survey_db -c "
       SELECT setval('survey_data_id_seq', (SELECT MAX(id) FROM survey_data));
     "

  2. To prevent this, use session ID or UUID:
     # Consider adding a session_id column

  3. Check for duplicates:
     $ psql -U postgres -d survey_db -c "
       SELECT COUNT(*) FROM survey_data;
     "


PROBLEM 9: "Disk space full"
============================

Symptoms:
  ✗ No space left on device
  ✗ Insert fails after certain number of rows

Solutions:
  1. Check disk usage:
     $ df -h

  2. Clean up:
     $ sudo apt-get clean
     $ rm -rf /tmp/*

  3. Expand partition:
     $ sudo lvm ...  (varies by setup)

  4. For PostgreSQL:
     $ sudo du -sh /var/lib/postgresql/


PROBLEM 10: "Column mismatch or data type errors"
=================================================

Symptoms:
  ✗ Some rows inserted, then type error
  ✗ Invalid JSON or JSONB error

Solutions:
  1. Verify CSV columns:
     $ head -1 data/survey_data.csv

  2. Check for special characters:
     $ grep -P -n "[\x80-\xFF]" data/survey_data.csv | head -5

  3. Manually test JSON conversion:
     ```python
     import json
     test_data = {"key": "value", "name": "test"}
     json_str = json.dumps(test_data)
     print(json_str)
     ```

  4. Check log file for specific row errors:
     $ grep "JSON conversion" csv_uploader.log
"""


# ============================================================================
# PERFORMANCE BENCHMARKS
# ============================================================================

BENCHMARKS = """

Expected Performance Metrics
=============================

Machine: Generic VM (4 CPU, 8GB RAM)
Database: PostgreSQL 14, local SSD
CSV File: ~1000 column, 1GB size

Settings           │ Chunk Size │ Speed       │ Memory    │ Time
─────────────────────┼────────────┼─────────────┼───────────┼──────────
Small (test)        │ 5,000      │ 500 rows/s  │ 50 MB     │ 4 min
Normal              │ 10,000     │ 1000 rows/s │ 100 MB    │ 2 min
Large (tuned)       │ 50,000     │ 2000 rows/s │ 500 MB    │ 1 min

Production Server: 32 CPU, 256GB RAM, NVMe SSD
PostgreSQL: Tuned for batch loading

Setting             │ Chunk Size │ Speed       │ Memory    │ 100GB File
─────────────────────┼────────────┼─────────────┼───────────┼──────────────
Optimized           │ 100,000    │ 5000 rows/s │ 1 GB      │ ~5.5 hours


Factors Affecting Speed
=======================

FAST (> 2000 rows/s):
  ✓ Chunk size: 50,000 - 100,000
  ✓ SSD storage
  ✓ Low_memory=False in pd.read_csv()
  ✓ Simple JSONB data (< 50KB per row)
  ✓ No complex indexes
  ✓ PostgreSQL work_mem > 256MB

SLOW (< 500 rows/s):
  ✗ Chunk size: 1,000 - 5,000
  ✗ HDD storage
  ✗ Network latency
  ✗ Large JSONB objects (> 1MB per row)
  ✗ Complex data types
  ✗ Other processes using disk
"""


# ============================================================================
# QUICK DIAGNOSTIC SCRIPT
# ============================================================================

DIAGNOSTIC_SCRIPT = """
# Copy this script as 'diagnose.py' and run:
# $ python diagnose.py

import os
import sys
import psycopg2

print("=" * 70)
print("DIAGNOSTIC CHECK")
print("=" * 70)

# 1. Check Python
print("\\n1. Python version:", sys.version.split()[0])

# 2. Check pandas
try:
    import pandas as pd
    print("2. pandas version:", pd.__version__)
except ImportError:
    print("2. ✗ pandas NOT installed")

# 3. Check psycopg2
try:
    import psycopg2
    print("3. psycopg2 version:", psycopg2.__version__)
except ImportError:
    print("3. ✗ psycopg2 NOT installed")

# 4. Test PostgreSQL connection
try:
    conn = psycopg2.connect(
        host='localhost', port=5432,
        database='survey_db', user='postgres', password='1234'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM survey_data;")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    print(f"4. Database 'survey_db' has {count:,} rows")
except Exception as e:
    print(f"4. ✗ Database connection failed: {e}")

# 5. Check test CSV
if os.path.exists('data/survey_data.csv'):
    size_mb = os.path.getsize('data/survey_data.csv') / (1024*1024)
    print(f"5. CSV file found: {size_mb:.2f} MB")
else:
    print("5. ✗ CSV file not found at data/survey_data.csv")

print("\\n" + "=" * 70)
"""


if __name__ == "__main__":
    print(TROUBLESHOOTING)
    print("\n" + "=" * 70 + "\n")
    print(BENCHMARKS)
