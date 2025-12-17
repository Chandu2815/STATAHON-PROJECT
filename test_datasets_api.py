"""
Test script to check datasets API and database connection
"""
import sys
sys.path.insert(0, 'C:/Users/Dell/OneDrive/Desktop/Chandu/STATATHON/Statathon 2')

from app.database import engine, SessionLocal, init_db
from app.models.dataset import Dataset
from sqlalchemy import inspect, text

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)

try:
    # Test connection
    with engine.connect() as conn:
        print(f"✓ Successfully connected to: {engine.url}")
        print()
        
        # Check if datasets table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📊 Available tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")
        print()
        
        # Check datasets table
        if 'datasets' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM datasets"))
            count = result.fetchone()[0]
            print(f"✓ datasets table exists with {count} records")
            
            # List all datasets
            result = conn.execute(text("SELECT id, name, table_name FROM datasets"))
            datasets = result.fetchall()
            if datasets:
                print("\n📋 Registered Datasets:")
                for ds in datasets:
                    print(f"  ID: {ds[0]}, Name: {ds[1]}, Table: {ds[2]}")
            else:
                print("⚠️  No datasets registered yet!")
        else:
            print("⚠️  datasets table does not exist!")
            print("   Run init_db() to create it")
        
        print()
        
        # Check if household_survey and person_survey tables exist
        plfs_tables = [t for t in tables if 'survey' in t.lower() or 'plfs' in t.lower()]
        if plfs_tables:
            print(f"✓ Found PLFS-related tables: {', '.join(plfs_tables)}")
            for table in plfs_tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                print(f"  - {table}: {count} rows")
        else:
            print("⚠️  No PLFS tables (household_survey, person_survey) found")
            
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPossible issues:")
    print("  - Database server not running")
    print("  - Incorrect DATABASE_URL in config")
    print("  - Database not initialized")

print()
print("=" * 60)
