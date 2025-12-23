import sqlite3

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

# Check what state code Jharkhand has
print("=" * 80)
print("Checking Jharkhand data in person_survey")
print("=" * 80)

# Jharkhand should be state code 20
cursor.execute('SELECT COUNT(*) FROM person_survey WHERE State_UT_Code = 20')
jharkhand_count = cursor.fetchone()[0]
print(f"Records for State_UT_Code = 20 (Jharkhand): {jharkhand_count}")

# Check with filters: Male (Sex=1), Age 15-29, Rural (Sector=1)
cursor.execute('''
    SELECT COUNT(*) FROM person_survey 
    WHERE State_UT_Code = 20 
    AND Sex = 1 
    AND Age BETWEEN 15 AND 29 
    AND Sector = 1
''')
filtered_count = cursor.fetchone()[0]
print(f"Jharkhand, Male, Age 15-29, Rural: {filtered_count}")

# Show sample records
print("\nSample Jharkhand records:")
cursor.execute('''
    SELECT State_UT_Code, District_Code, Sector, Sex, Age, Principal_Status_Code
    FROM person_survey 
    WHERE State_UT_Code = 20 
    AND Sex = 1 
    AND Age BETWEEN 15 AND 29 
    AND Sector = 1
    LIMIT 5
''')
for row in cursor.fetchall():
    print(f"  State={row[0]}, District={row[1]}, Sector={row[2]}, Sex={row[3]}, Age={row[4]}, Status={row[5]}")

# Check what states we have
print("\n" + "=" * 80)
print("Available states in person_survey:")
print("=" * 80)
cursor.execute('SELECT DISTINCT State_UT_Code FROM person_survey ORDER BY State_UT_Code')
states = [row[0] for row in cursor.fetchall()]
print(f"State codes: {states}")

conn.close()
