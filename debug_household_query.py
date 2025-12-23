import sqlite3

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

print("=" * 80)
print("DEBUGGING HOUSEHOLD SURVEY QUERY")
print("=" * 80)

# Check Chhattisgarh data - State code 22
print("\n1. Checking Chhattisgarh data:")
print("-" * 80)

cursor.execute('SELECT COUNT(*) FROM household_survey WHERE State_Ut_Code = 22')
chhattisgarh_count = cursor.fetchone()[0]
print(f"Total Chhattisgarh records: {chhattisgarh_count}")

# Check with sector filter (Rural = 1)
cursor.execute('SELECT COUNT(*) FROM household_survey WHERE State_Ut_Code = 22 AND Sector = 1')
rural_count = cursor.fetchone()[0]
print(f"Chhattisgarh + Rural: {rural_count}")

# Check what columns household_survey has
print("\n2. Checking household_survey columns:")
print("-" * 80)
cursor.execute('PRAGMA table_info(household_survey)')
columns = [col[1] for col in cursor.fetchall()]

has_sex = 'Sex' in columns or 'Gender' in columns
has_age = 'Age' in columns or 'Age_Group' in columns

print(f"Has 'Sex' or 'Gender' column: {has_sex}")
print(f"Has 'Age' or 'Age_Group' column: {has_age}")

if not has_sex:
    print("⚠ WARNING: Household Survey does NOT have Gender/Sex column!")
if not has_age:
    print("⚠ WARNING: Household Survey does NOT have Age column!")

# Show sample Chhattisgarh records
print("\n3. Sample Chhattisgarh household records:")
print("-" * 80)
cursor.execute('''
    SELECT State_Ut_Code, District_Code, Sector, Household_Size, 
           Monthly_Consumer_Expenditure, Religion, Social_Group
    FROM household_survey 
    WHERE State_Ut_Code = 22 AND Sector = 1
    LIMIT 5
''')
for row in cursor.fetchall():
    print(f"State={row[0]}, District={row[1]}, Sector={row[2]}, Size={row[3]}, Expenditure=₹{row[4]}, Religion={row[5]}, SocialGroup={row[6]}")

# Check available states
print("\n4. Available states in household_survey:")
print("-" * 80)
cursor.execute('SELECT DISTINCT State_Ut_Code FROM household_survey ORDER BY State_Ut_Code')
states = [row[0] for row in cursor.fetchall()]
print(f"State codes: {states}")

if 22 in states:
    print("✓ Chhattisgarh (code 22) exists in database")
else:
    print("✗ Chhattisgarh (code 22) NOT FOUND")

print("\n" + "=" * 80)
print("ISSUE IDENTIFIED:")
print("=" * 80)
print("The Household Survey query is showing Gender and Age filters,")
print("but household_survey table does NOT have these columns!")
print("These filters only apply to Person Survey (individual-level data).")
print("\nThe backend is likely ignoring these filters or failing the query.")
print("=" * 80)

conn.close()
