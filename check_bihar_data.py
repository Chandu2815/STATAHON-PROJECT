from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Check if there's any data with State_Ut_Code=10 (Bihar)
result = db.execute(text('SELECT COUNT(*) FROM household_survey WHERE "State_Ut_Code" = 10')).fetchone()
print(f'Records with State_Ut_Code=10 (Bihar): {result[0]}')

# Check data with State_Ut_Code=28 
result28 = db.execute(text('SELECT COUNT(*) FROM household_survey WHERE "State_Ut_Code" = 28')).fetchone()
print(f'Records with State_Ut_Code=28 (Andhra Pradesh): {result28[0]}')

# Check what state codes exist for Male, Age 15-29
result_filtered = db.execute(text('''
    SELECT DISTINCT "State_Ut_Code", COUNT(*) as count 
    FROM household_survey 
    WHERE "Sex" = 1 AND "Age" BETWEEN 15 AND 29
    GROUP BY "State_Ut_Code"
    ORDER BY "State_Ut_Code"
    LIMIT 10
''')).fetchall()
print('\nState codes with Male, Age 15-29:')
for row in result_filtered:
    print(f'  State_Ut_Code={row[0]}: {row[1]} records')

db.close()
