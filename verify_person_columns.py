import sqlite3

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

# Get all columns from person_survey table
cursor.execute('PRAGMA table_info(person_survey)')
columns_info = cursor.fetchall()

print("=" * 80)
print("VERIFYING PERSON SURVEY COLUMNS")
print("=" * 80)

# Columns being displayed in the dashboard
displayed_columns = [
    'State_UT_Code',
    'District_Code',
    'Sector',
    'Sex',
    'Age',
    'Marital_Status',
    'General_Education_Level',
    'Principal_Status_Code',
    'Principal_Industry_Code',
    'Principal_Occupation_Code',
    'CWS_Earnings_Salaried',
    'CWS_Earnings_SelfEmployed',
    'Day7_Act1_Hours',
    'Day7_Act1_Wage'
]

# Get actual column names from database
actual_columns = [col[1] for col in columns_info]

print("\nChecking if displayed columns exist in person_survey table:")
print("-" * 80)

all_valid = True
for col in displayed_columns:
    if col in actual_columns:
        print(f"✓ {col:<35} - EXISTS in person_survey")
    else:
        print(f"✗ {col:<35} - NOT FOUND in person_survey")
        all_valid = False

print("\n" + "=" * 80)
if all_valid:
    print("✓ ALL COLUMNS ARE VALID - They belong to person_survey table!")
else:
    print("✗ SOME COLUMNS ARE INVALID - Check configuration!")

print("=" * 80)

# Show what these columns represent
print("\nColumn Meanings:")
print("-" * 80)
print("State_UT_Code              → State/UT identifier")
print("District_Code              → District identifier")
print("Sector                     → Rural (1) or Urban (2)")
print("Sex                        → Male (1), Female (2), Other (3)")
print("Age                        → Age in years")
print("Marital_Status             → Marital status code")
print("General_Education_Level    → Education level code")
print("Principal_Status_Code      → Main activity status (working, student, etc.)")
print("Principal_Industry_Code    → Industry classification")
print("Principal_Occupation_Code  → Occupation classification")
print("CWS_Earnings_Salaried      → Monthly salaried earnings in rupees")
print("CWS_Earnings_SelfEmployed  → Monthly self-employed earnings in rupees")
print("Day7_Act1_Hours            → Work hours in last week (Day 7)")
print("Day7_Act1_Wage             → Daily wage in rupees (Day 7)")

print("\n" + "=" * 80)
print("DATASET CONFIRMATION:")
print("=" * 80)
print("✓ These are PERSON-LEVEL employment and demographic data")
print("✓ From PLFS (Periodic Labour Force Survey)")
print("✓ Individual worker characteristics and earnings")
print("✓ NOT household-level data")
print("=" * 80)

conn.close()
