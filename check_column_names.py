from app.database import SessionLocal
from sqlalchemy import inspect

db = SessionLocal()
inspector = inspect(db.bind)

# Get all column names from household_survey table
columns = inspector.get_columns('household_survey')
print('Columns in household_survey table:')
for col in columns:
    if 'state' in col['name'].lower() or 'sex' in col['name'].lower() or 'age' in col['name'].lower():
        print(f'  {col["name"]} ({col["type"]})')

db.close()
