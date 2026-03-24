#!/usr/bin/env python3
"""
ROBUST CSV TO POSTGRESQL UPLOADER
Quick Start Guide

This script provides a simple step-by-step guide to get started.
"""

import os
import sys
from csv_uploader_robust import RobustCSVUploader


def print_header():
    """Print welcome header."""
    print("\n" + "=" * 80)
    print(" " * 15 + "ROBUST CSV TO POSTGRESQL UPLOADER")
    print("=" * 80)


def print_requirements():
    """Print system requirements."""
    print("\n📋 REQUIREMENTS:")
    print("  ✓ Python 3.8+")
    print("  ✓ PostgreSQL 12+")
    print("  ✓ pandas >= 1.3.0")
    print("  ✓ psycopg2-binary >= 2.9.0")


def check_environment():
    """Check if environment is properly set up."""
    print("\n🔍 CHECKING ENVIRONMENT...")
    
    errors = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        errors.append("Python 3.8+ required")
    else:
        print(f"  ✓ Python {sys.version.split()[0]}")
    
    # Check pandas
    try:
        import pandas as pd
        print(f"  ✓ pandas {pd.__version__}")
    except ImportError:
        errors.append("pandas not installed - run: pip install pandas")
    
    # Check psycopg2
    try:
        import psycopg2
        print(f"  ✓ psycopg2-binary installed")
    except ImportError:
        errors.append("psycopg2-binary not installed - run: pip install psycopg2-binary")
    
    # Check PostgreSQL connection
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='survey_db',
            user='postgres',
            password='1234',
            connect_timeout=3
        )
        conn.close()
        print("  ✓ PostgreSQL connection works")
    except Exception as e:
        errors.append(f"PostgreSQL connection failed: {str(e)[:50]}")
    
    if errors:
        print("\n❌ ISSUES FOUND:")
        for err in errors:
            print(f"  ✗ {err}")
        return False
    
    print("\n✅ All checks passed!")
    return True


def print_setup_instructions():
    """Print setup instructions."""
    print("\n📝 SETUP INSTRUCTIONS:")
    print("""
1. INSTALL DEPENDENCIES:
   $ pip install pandas psycopg2-binary

2. ENSURE POSTGRESQL IS RUNNING:
   $ sudo systemctl status postgresql
   
   If not running:
   $ sudo systemctl start postgresql

3. CREATE DATABASE (if not exists):
   $ psql -U postgres -c "CREATE DATABASE survey_db;"

4. PREPARE CSV FILE:
   - Place your CSV file in: data/survey_data.csv
   - Or update the file path in the script

5. VERIFY CSV FORMAT:
   $ head -5 data/survey_data.csv
   
   File should have:
   - UTF-8 or latin1 encoding (auto-detected)
   - Consistent column structure
   - No corrupt rows
    """)


def print_usage_examples():
    """Print usage examples."""
    print("\n💡 BASIC USAGE EXAMPLES:")
    print("""
# Example 1: Default settings
uploader = RobustCSVUploader()
uploader.upload_csv('data/survey_data.csv')

# Example 2: Custom configuration
uploader = RobustCSVUploader(
    host='localhost',
    port=5432,
    database='survey_db',
    user='postgres',
    password='1234',
    chunksize=5000
)
success = uploader.upload_csv('data/survey_data.csv')
stats = uploader.get_statistics()
print(f"Inserted: {stats['total_inserted']:,} rows")

# Example 3: Large file (50GB+)
uploader = RobustCSVUploader(chunksize=50000)
uploader.upload_csv('data/large_dataset.csv')
    """)


def print_key_features():
    """Print key features."""
    print("\n⭐ KEY FEATURES:")
    print("""
✓ Chunk Processing     - Memory-efficient for files up to 100GB+
✓ Encoding Detection   - Auto-detects UTF-8, falls back to latin1
✓ Null Handling        - Removes null values before JSON conversion
✓ Bulk Insert          - Uses executemany() for optimal performance
✓ Error Recovery       - Skips bad rows, continues processing
✓ Progress Tracking    - Real-time logging of rows inserted
✓ Connection Safety    - Proper cleanup and transaction management
✓ Statistics           - Detailed upload metrics (speed, count, etc.)
    """)


def print_performance_tips():
    """Print performance tips."""
    print("\n⚡ PERFORMANCE TIPS:")
    print("""
MEMORY USAGE:
  - Chunk size 5000   ≈ 50 MB per batch
  - Chunk size 10000  ≈ 100 MB per batch
  - Chunk size 50000  ≈ 500 MB per batch

FOR FASTER INSERTS:
  1. Use larger chunk size (if RAM available)
  2. Ensure PostgreSQL uses SSD storage
  3. Pre-clean CSV to remove bad rows
  4. Use low_memory=False (enabled automatically)

FOR LARGE FILES (100GB+):
  1. Use machine with 32GB+ RAM
  2. Set chunk size to 50000-100000
  3. Disable autovacuum during insert
  4. Consider splitting into multiple files
    """)


def print_troubleshooting():
    """Print common troubleshooting tips."""
    print("\n🔧 TROUBLESHOOTING:")
    print("""
COMMON ISSUES:
  
  "Failed to connect": 
    - Ensure PostgreSQL is running
    - Check credentials (host, port, user, password)
    - Verify database exists

  "Out of memory":
    - Reduce chunk size (e.g., from 50000 to 5000)
    - Close other applications
    
  "UTF-8 decode error":
    - Automatic fallback to latin1 enabled
    - Or convert CSV: iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv
    
  "Slow inserts":
    - Increase chunk size
    - Use SSD storage
    - Check CSV file for corrupted rows

For detailed troubleshooting, see: csv_uploader_troubleshooting.py
    """)


def print_logging_info():
    """Print logging information."""
    print("\n📊 LOGGING:")
    print("""
Logs are written to: csv_uploader.log

Monitor progress in real-time:
  $ tail -f csv_uploader.log

View final summary:
  $ tail -n 20 csv_uploader.log

Check for errors:
  $ grep ERROR csv_uploader.log
    """)


def print_next_steps():
    """Print next steps."""
    print("\n🚀 NEXT STEPS:")
    print("""
1. QUICK TEST (100 rows):
   - Create test CSV with first 100 rows
   - Run uploader
   - Verify rows in database:
     psql -U postgres -d survey_db -c "SELECT COUNT(*) FROM survey_data;"

2. FULL RUN:
   - Copy example code from csv_uploader_robust_examples.py
   - Modify file path to your CSV
   - Run: python -c "from csv_uploader_robust import ...; uploader.upload_csv(...)"

3. PRODUCTION USE:
   - Review all settings
   - Test with sample data first
   - Use appropriate chunk size for your RAM
   - Monitor logs during upload
    """)


def print_file_locations():
    """Print important file locations."""
    print("\n📁 FILE LOCATIONS:")
    print("""
Main Files:
  - csv_uploader_robust.py              Main uploader class
  - csv_uploader_robust_examples.py     Usage examples
  - csv_uploader_troubleshooting.py     Troubleshooting guide

Usage:
  from csv_uploader_robust import RobustCSVUploader
  uploader = RobustCSVUploader()
  uploader.upload_csv('data/survey_data.csv')

Logs:
  - csv_uploader.log                    Real-time logs
    """)


def main():
    """Main quick start function."""
    print_header()
    print_requirements()
    
    if not check_environment():
        print("\n⚠️  Please fix the issues above and try again.")
        print("   See: csv_uploader_troubleshooting.py for help")
        return 1
    
    print_setup_instructions()
    print_key_features()
    print_usage_examples()
    print_performance_tips()
    print_troubleshooting()
    print_logging_info()
    print_file_locations()
    print_next_steps()
    
    print("\n" + "=" * 80)
    print("✅ QUICK START GUIDE COMPLETE")
    print("=" * 80)
    print("\nFor examples, run:")
    print("  $ python csv_uploader_robust_examples.py")
    print("\nFor full documentation, see:")
    print("  $ python csv_uploader_troubleshooting.py")
    print("\n" + "=" * 80 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
