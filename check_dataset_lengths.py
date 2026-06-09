from app.database import SessionLocal
from app.models.dataset import Dataset
from sqlalchemy import text

db = SessionLocal()

print("Dataset Record Counts:")
print("=" * 60)

# Check household_survey
count = db.execute(text('SELECT COUNT(*) FROM household_survey')).fetchone()[0]
print(f"Household Survey (PLFS): {count:,} records")

# Check person_survey
count = db.execute(text('SELECT COUNT(*) FROM person_survey')).fetchone()[0]
print(f"Person Survey (PLFS): {count:,} records")

# Check datasets stored in data_records
datasets = db.query(Dataset).filter(Dataset.table_name == None).all()
for dataset in datasets:
    count = db.execute(text(f'SELECT COUNT(*) FROM data_records WHERE dataset_id = {dataset.id}')).fetchone()[0]
    print(f"{dataset.name}: {count:,} records")

print("=" * 60)

# Also show state distribution in household_survey
print("\nState Distribution in Household Survey:")
result = db.execute(text('''
    SELECT "State_Ut_Code", COUNT(*) as count 
    FROM household_survey 
    GROUP BY "State_Ut_Code" 
    ORDER BY "State_Ut_Code"
''')).fetchall()

for row in result:
    print(f"  State Code {row[0]:2d}: {row[1]:,} records")

db.close()
