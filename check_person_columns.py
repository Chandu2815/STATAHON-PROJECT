import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('mospi_dpi.db')

# Get actual column names from person_survey table
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(person_survey)')
columns = cursor.fetchall()

print("Person Survey Table Columns:")
print("=" * 80)
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check a sample record with non-zero earnings
print("\n" + "=" * 80)
print("Sample records with non-zero earnings:")
print("=" * 80)

query = """
SELECT 
    State_UT_Code, District_Code, Sector, Sex, Age, 
    Marital_Status, General_Education_Level,
    Principal_Status_Code, Principal_Industry_Code, Principal_Occupation_Code,
    CWS_Status_Code, CWS_Earnings_Salaried, CWS_Earnings_SelfEmployed,
    Day7_Act1_Hours, Day7_Act1_Wage
FROM person_survey 
WHERE CWS_Earnings_Salaried > 0 OR CWS_Earnings_SelfEmployed > 0
LIMIT 5
"""

df = pd.read_sql_query(query, conn)
print(df.to_string())

# Check the records matching the screenshot (State=36, Age=15, Rural, Male)
print("\n" + "=" * 80)
print("Records matching screenshot (State=36, Age=15, Sector=1/Rural, Sex=1/Male):")
print("=" * 80)

query2 = """
SELECT 
    State_UT_Code, District_Code, Sector, Sex, Age, 
    Marital_Status, General_Education_Level,
    Principal_Status_Code, Principal_Industry_Code, Principal_Occupation_Code,
    CWS_Status_Code, CWS_Earnings_Salaried, CWS_Earnings_SelfEmployed,
    Day7_Act1_Hours, Day7_Act1_Wage
FROM person_survey 
WHERE State_UT_Code = 36 AND Age = 15 AND Sector = 1 AND Sex = 1
LIMIT 10
"""

df2 = pd.read_sql_query(query2, conn)
print(df2.to_string())

# Check overall statistics for earnings
print("\n" + "=" * 80)
print("Overall earnings statistics:")
print("=" * 80)

cursor.execute("""
    SELECT 
        COUNT(*) as total_records,
        COUNT(CASE WHEN CWS_Earnings_Salaried > 0 THEN 1 END) as non_zero_salaried,
        COUNT(CASE WHEN CWS_Earnings_SelfEmployed > 0 THEN 1 END) as non_zero_self_employed,
        AVG(CASE WHEN CWS_Earnings_Salaried > 0 THEN CWS_Earnings_Salaried END) as avg_salaried,
        AVG(CASE WHEN CWS_Earnings_SelfEmployed > 0 THEN CWS_Earnings_SelfEmployed END) as avg_self_employed
    FROM person_survey
""")
stats = cursor.fetchone()
print(f"  Total records: {stats[0]}")
print(f"  Non-zero salaried earnings: {stats[1]}")
print(f"  Non-zero self-employed earnings: {stats[2]}")
print(f"  Average salaried (when > 0): ₹{stats[3]:.2f}" if stats[3] else "  Average salaried: N/A")
print(f"  Average self-employed (when > 0): ₹{stats[4]:.2f}" if stats[4] else "  Average self-employed: N/A")

conn.close()
