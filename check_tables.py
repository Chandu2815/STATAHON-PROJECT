from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# PostgreSQL: list tables in public schema
result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name")).fetchall()
print("Available tables:")
for r in result:
    print(f"  - {r[0]}")

# Check record counts
for table_name in [r[0] for r in result]:
    try:
        count = db.execute(text(f"SELECT COUNT(*) FROM \"{table_name}\"" )).fetchone()[0]
        print(f"{table_name}: {count} records")
    except Exception as e:
        print(f"{table_name}: Error - {e}")

db.close()
