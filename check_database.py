"""Quick check of database tables and data"""
from app.database import engine
from sqlalchemy import text, inspect

# Get table names
inspector = inspect(engine)
tables = inspector.get_table_names()

print("="*60)
print("DATABASE STATUS")
print("="*60)
print(f"\nTables found: {len(tables)}")
for table in tables:
    print(f"  - {table}")

# Check household_survey if it exists
if 'household_survey' in tables:
    with engine.connect() as conn:
        # Count rows
        result = conn.execute(text("SELECT COUNT(*) FROM household_survey"))
        count = result.scalar()
        print(f"\nHousehold Survey Table:")
        print(f"  Rows: {count:,}")
        
        # Get column info
        columns = inspector.get_columns('household_survey')
        print(f"  Columns: {len(columns)}")
        
        # Sample data if any
        if count > 0:
            result = conn.execute(text("SELECT * FROM household_survey LIMIT 3"))
            rows = result.fetchall()
            print(f"\n  Sample data (first 3 rows):")
            for i, row in enumerate(rows, 1):
                print(f"    Row {i}: {dict(row._mapping)}")

# Check datasets table
if 'datasets' in tables:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name, table_name FROM datasets"))
        datasets = result.fetchall()
        print(f"\nRegistered Datasets: {len(datasets)}")
        for ds in datasets:
            print(f"  ID {ds[0]}: {ds[1]} -> {ds[2]}")

print("\n" + "="*60)
