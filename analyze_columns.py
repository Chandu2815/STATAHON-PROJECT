from app.database import SessionLocal
from sqlalchemy import inspect, text

db = SessionLocal()
inspector = inspect(db.bind)

print("="*80)
print("HOUSEHOLD SURVEY COLUMNS")
print("="*80)
columns = inspector.get_columns('household_survey')
for i, col in enumerate(columns, 1):
    print(f"{i:3d}. {col['name']:40s} {str(col['type']):20s}")

# Sample data to understand values
print("\n" + "="*80)
print("HOUSEHOLD SURVEY SAMPLE DATA (First 3 records)")
print("="*80)
result = db.execute(text('SELECT * FROM household_survey LIMIT 3')).fetchall()
if result:
    for row in result:
        row_dict = dict(row._mapping)
        for key, value in list(row_dict.items())[:15]:  # First 15 columns
            print(f"  {key}: {value}")
        print()

print("\n" + "="*80)
print("PERSON SURVEY COLUMNS")
print("="*80)
columns = inspector.get_columns('person_survey')
for i, col in enumerate(columns, 1):
    print(f"{i:3d}. {col['name']:40s} {str(col['type']):20s}")

# Sample data to understand values
print("\n" + "="*80)
print("PERSON SURVEY SAMPLE DATA (First 3 records)")
print("="*80)
result = db.execute(text('SELECT * FROM person_survey LIMIT 3')).fetchall()
if result:
    for row in result:
        row_dict = dict(row._mapping)
        for key, value in list(row_dict.items())[:15]:  # First 15 columns
            print(f"  {key}: {value}")
        print()

# Get distinct values for key fields
print("\n" + "="*80)
print("KEY FIELD VALUE RANGES")
print("="*80)

print("\nSex values in person_survey:")
result = db.execute(text('SELECT DISTINCT "Sex" FROM person_survey ORDER BY "Sex"')).fetchall()
for row in result:
    print(f"  Sex = {row[0]}")

print("\nAge range in person_survey:")
result = db.execute(text('SELECT MIN("Age"), MAX("Age") FROM person_survey')).fetchone()
print(f"  Min Age: {result[0]}, Max Age: {result[1]}")

print("\nSector values (Rural/Urban):")
result = db.execute(text('SELECT DISTINCT "Sector" FROM household_survey ORDER BY "Sector"')).fetchall()
for row in result:
    print(f"  Sector = {row[0]}")

db.close()
