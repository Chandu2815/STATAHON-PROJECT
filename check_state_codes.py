"""Check state codes in the database"""
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=== State codes in household_survey ===")
result = db.execute(text('SELECT DISTINCT "State_UT_Code" FROM household_survey ORDER BY "State_UT_Code"'))
codes = [r[0] for r in result]
print("State codes:", codes)

print("\n=== State codes in person_survey ===")
result2 = db.execute(text('SELECT DISTINCT "State_UT_Code" FROM person_survey ORDER BY "State_UT_Code"'))
codes2 = [r[0] for r in result2]
print("State codes:", codes2)

print("\n=== District codes dataset (reference) ===")
# Check if we have district codes in data_records
result3 = db.execute(text("""
    SELECT data 
    FROM data_records 
    WHERE dataset_id = 2 
    LIMIT 10
"""))
for row in result3:
    print(row[0])

db.close()
