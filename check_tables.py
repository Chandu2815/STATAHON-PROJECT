from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
print("Available tables:")
for r in result:
    print(f"  - {r[0]}")
    
# Check record counts
for table_name in [r[0] for r in result]:
    try:
        count = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()[0]
        print(f"{table_name}: {count} records")
    except Exception as e:
        print(f"{table_name}: Error - {e}")

db.close()
