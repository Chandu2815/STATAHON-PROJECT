import sqlite3

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

# Check person_survey table structure
print("Person Survey Table Columns:")
print("=" * 70)

cursor.execute('PRAGMA table_info(person_survey)')
cols = cursor.fetchall()

# Find relevant columns for the query
relevant = ['state', 'district', 'sex', 'gender', 'age', 'male', 'female']
matching_cols = []

for col in cols:
    col_name = col[1].lower()
    if any(keyword in col_name for keyword in relevant):
        matching_cols.append(col[1])
        print(f"  {col[1]} ({col[2]})")

print(f"\n{'='*70}")
print("Sample query to test:")
print("  State: TELANGANA (need State_UT_Code = 36)")
print("  District: NIRMAL (need District_Code)")
print("  Gender: MALE (need Sex = 1)")
print("  Age: 15-29 (need Age between 15 and 29)")

# Check if we have Telangana data
print(f"\n{'='*70}")
print("Checking for Telangana data...")
cursor.execute('SELECT COUNT(*) FROM person_survey WHERE State_UT_Code = "36"')
count = cursor.fetchone()[0]
print(f"  Records with State_UT_Code=36 (Telangana): {count}")

# Check district codes in Telangana
cursor.execute('SELECT DISTINCT District_Code FROM person_survey WHERE State_UT_Code = "36" LIMIT 10')
districts = cursor.fetchall()
print(f"  Sample Telangana district codes: {[d[0] for d in districts]}")

# Check if Nirmal exists
cursor.execute('SELECT COUNT(*) FROM person_survey WHERE State_UT_Code = "36" AND District_Code = "04"')
nirmal_count = cursor.fetchone()[0]
print(f"  Records in Nirmal (code 04): {nirmal_count}")

# Check Sex values
cursor.execute('SELECT DISTINCT Sex FROM person_survey LIMIT 5')
sex_values = cursor.fetchall()
print(f"  Sex values in table: {[s[0] for s in sex_values]}")

# Check Age range
cursor.execute('SELECT MIN(Age), MAX(Age) FROM person_survey')
age_range = cursor.fetchone()
print(f"  Age range: {age_range[0]} to {age_range[1]}")

conn.close()
