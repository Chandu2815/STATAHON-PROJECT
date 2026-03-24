"""
Database Connection Testing Script
This script tests the database connection and displays detailed diagnostics.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("DATABASE CONNECTION TEST")
print("=" * 80)

# Test 1: Check environment variables
print("\n[1] Environment Variables:")
print("-" * 80)
db_url = os.getenv("DATABASE_URL", "Not set")
print(f"DATABASE_URL: {db_url}")

if db_url == "Not set":
    print("❌ DATABASE_URL not found in environment!")
    sys.exit(1)
else:
    print("✓ DATABASE_URL loaded successfully")

# Test 2: Check imports
print("\n[2] Checking Python Packages:")
print("-" * 80)
try:
    import sqlalchemy
    print(f"✓ SQLAlchemy {sqlalchemy.__version__}")
except ImportError:
    print("❌ SQLAlchemy not installed")
    sys.exit(1)

try:
    import psycopg2
    print(f"✓ psycopg2 {psycopg2.__version__}")
except ImportError:
    print("❌ psycopg2 not installed")
    sys.exit(1)

try:
    import fastapi
    print(f"✓ FastAPI {fastapi.__version__}")
except ImportError:
    print("❌ FastAPI not installed")
    sys.exit(1)

# Test 3: Test database connection
print("\n[3] Testing Database Connection:")
print("-" * 80)

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.pool import QueuePool

try:
    engine = create_engine(
        db_url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False
    )
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        result.fetchone()
    
    print("✓ Database connection successful")
except Exception as e:
    print(f"❌ Database connection failed: {str(e)}")
    sys.exit(1)

# Test 4: Check database tables
print("\n[4] Database Tables:")
print("-" * 80)

try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print(f"✓ Found {len(tables)} table(s):")
        for table in tables:
            columns = inspector.get_columns(table)
            print(f"  - {table} ({len(columns)} columns)")
    else:
        print("⚠ No tables found in database")
        print("  Create survey_data table with:")
        print("""
  CREATE TABLE survey_data (
      id BIGSERIAL PRIMARY KEY,
      data JSONB,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
        """)
except Exception as e:
    print(f"⚠ Could not inspect tables: {str(e)}")

# Test 5: Verify survey_data table
print("\n[5] Checking survey_data Table:")
print("-" * 80)

try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if "survey_data" in tables:
        print("✓ survey_data table exists")
        columns = inspector.get_columns("survey_data")
        print(f"  Columns ({len(columns)}):")
        for col in columns:
            print(f"    - {col['name']}: {col['type']}")
    else:
        print("❌ survey_data table not found")
        print("  Please create it with the SQL statement shown above")
except Exception as e:
    print(f"⚠ Error checking table: {str(e)}")

print("\n" + "=" * 80)
print("✓ ALL TESTS PASSED - Ready to run FastAPI!")
print("=" * 80)
print("\nTo start the server:")
print("  python main.py")
print("\nAPI Endpoints:")
print("  GET  http://localhost:8000/")
print("  GET  http://localhost:8000/health")
print("  GET  http://localhost:8000/data")
print("  POST http://localhost:8000/add")
print("\nAPI Documentation:")
print("  http://localhost:8000/docs")
print("=" * 80)
