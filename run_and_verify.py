#!/usr/bin/env python3
"""
Run & Verify Script for CSV Uploader
Complete end-to-end testing and verification
"""

import subprocess
import sys
import os
import psycopg2
from datetime import datetime


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def check_prerequisites():
    """Check if all prerequisites are met."""
    print_section("✓ CHECKING PREREQUISITES")
    
    errors = []
    
    # Check Python
    print(f"  Python: {sys.version.split()[0]} ✓")
    
    # Check pandas
    try:
        import pandas as pd
        print(f"  pandas: {pd.__version__} ✓")
    except ImportError:
        errors.append("pandas not installed")
    
    # Check psycopg2
    try:
        import psycopg2
        print(f"  psycopg2: installed ✓")
    except ImportError:
        errors.append("psycopg2 not installed")
    
    # Check PostgreSQL connection
    try:
        conn = psycopg2.connect(
            host='187.127.138.4',
            port=5432,
            database='statahon_db',
            user='postgres',
            password='NewPassword123',
            connect_timeout=3
        )
        conn.close()
        print(f"  PostgreSQL: connected ✓")
    except Exception as e:
        errors.append(f"PostgreSQL connection failed: {str(e)[:50]}")
    
    if errors:
        print("\n  ❌ ISSUES FOUND:")
        for err in errors:
            print(f"    - {err}")
        return False
    
    print("\n  ✅ All prerequisites OK!")
    return True


def verify_postgres_empty():
    """Verify survey_data table is empty before upload."""
    print_section("📊 VERIFYING DATABASE STATE")
    
    try:
        conn = psycopg2.connect(
            host='187.127.138.4',
            port=5432,
            database='statahon_db',
            user='postgres',
            password='NewPassword123'
        )
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'survey_data'
            )
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("  Table 'survey_data' does not exist (will be created)")
            cursor.close()
            conn.close()
            return True
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM survey_data")
        row_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"  Current rows in database: {row_count:,}")
        
        if row_count > 0:
            print(f"  ⚠ Warning: Table has {row_count:,} existing rows")
            response = input("  Continue with upload? (y/n): ")
            return response.lower() == 'y'
        
        return True
    
    except Exception as e:
        print(f"  ⚠ Could not verify: {e}")
        return True


def run_uploader():
    """Run the CSV uploader."""
    print_section("🚀 RUNNING CSV UPLOADER")
    
    try:
        # Run the uploader
        result = subprocess.run(
            ['python', 'csv_uploader.py'],
            capture_output=False,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print("\n  ❌ Upload timed out")
        return False
    except Exception as e:
        print(f"\n  ❌ Error running uploader: {e}")
        return False


def verify_upload_results():
    """Verify results after upload."""
    print_section("✓ VERIFYING UPLOAD RESULTS")
    
    try:
        conn = psycopg2.connect(
            host='187.127.138.4',
            port=5432,
            database='statahon_db',
            user='postgres',
            password='NewPassword123'
        )
        cursor = conn.cursor()
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM survey_data")
        total_rows = cursor.fetchone()[0]
        
        print(f"\n  Total rows in survey_data: {total_rows:,} ✓")
        
        if total_rows == 0:
            print("  ⚠ No rows were inserted")
            return False
        
        # Get sample rows
        cursor.execute("SELECT id, data, created_at FROM survey_data LIMIT 3")
        samples = cursor.fetchall()
        
        print(f"\n  Sample rows:")
        for row in samples:
            print(f"    ID: {row[0]} | Created: {row[2]}")
        
        # Get data structure sample
        cursor.execute("SELECT jsonb_keys(data) FROM survey_data WHERE data IS NOT NULL LIMIT 1")
        keys = cursor.fetchone()
        if keys:
            print(f"\n  JSON keys in data: {keys[0][:3]}...")  # Show first 3 keys
        
        cursor.close()
        conn.close()
        
        print(f"\n  ✅ Upload verification successful!")
        return True
    
    except Exception as e:
        print(f"\n  ❌ Verification failed: {e}")
        return False


def print_summary(success, initial_count, final_count):
    """Print final summary."""
    print_section("📋 FINAL SUMMARY")
    
    if success:
        rows_added = final_count - initial_count
        print(f"\n  ✅ UPLOAD SUCCESSFUL!")
        print(f"     Initial rows: {initial_count:,}")
        print(f"     Final rows: {final_count:,}")
        print(f"     Rows added: {rows_added:,}")
        print(f"\n  You can query the data:")
        print(f"    psql -U postgres -h 187.127.138.4 -d statahon_db -c 'SELECT COUNT(*) FROM survey_data;'")
        print(f"    psql -U postgres -h 187.127.138.4 -d statahon_db -c 'SELECT * FROM survey_data LIMIT 5;'")
    else:
        print(f"\n  ❌ UPLOAD FAILED")
        print(f"     Check logs: tail -f /tmp/csv_uploader.log")
    
    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "CSV UPLOADER - RUN & VERIFY" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n  Please install missing dependencies and try again.")
        return 1
    
    # Step 2: Verify database state
    if not verify_postgres_empty():
        print("\n  Upload cancelled.")
        return 1
    
    # Get initial count
    try:
        conn = psycopg2.connect(
            host='187.127.138.4',
            port=5432,
            database='statahon_db',
            user='postgres',
            password='NewPassword123'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM survey_data")
        initial_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
    except:
        initial_count = 0
    
    # Step 3: Run uploader
    if not run_uploader():
        print_summary(False, initial_count, initial_count)
        return 1
    
    # Step 4: Verify results
    if not verify_upload_results():
        print_summary(False, initial_count, initial_count)
        return 1
    
    # Get final count
    try:
        conn = psycopg2.connect(
            host='187.127.138.4',
            port=5432,
            database='statahon_db',
            user='postgres',
            password='NewPassword123'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM survey_data")
        final_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
    except:
        final_count = initial_count
    
    # Step 5: Print summary
    print_summary(True, initial_count, final_count)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
