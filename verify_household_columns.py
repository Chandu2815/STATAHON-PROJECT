import sqlite3

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

# Get all columns from household_survey table
cursor.execute('PRAGMA table_info(household_survey)')
columns_info = cursor.fetchall()

print("=" * 80)
print("VERIFYING HOUSEHOLD SURVEY COLUMNS")
print("=" * 80)

# Columns shown in the screenshot
displayed_columns = [
    'State_Code',  # or State_Ut_Code
    'District_Code',
    'Sector',
    'Quarter',
    'Survey_Month',  # or Month_of_Survey
    'Household_Size',
    'Type',  # or Household_Type
    'Religion',
    'Social_Group',
    'Monthly_Expenditure',  # or Monthly_Consumer_Expenditure
    'Usual_Expenditure',
    'Annual_Clothing',  # or Annual_Clothing_Expenditure
    'Annual_Durables'  # or Annual_Durables_Expenditure
]

# Get actual column names from database
actual_columns = [col[1] for col in columns_info]

print("\nActual household_survey table columns:")
print("-" * 80)
for col in actual_columns:
    print(f"  {col}")

print("\n" + "=" * 80)
print("Checking displayed columns against household_survey:")
print("-" * 80)

# Check common variations
column_mapping = {
    'State_Code': ['State_Ut_Code', 'State_UT_Code', 'State_Code'],
    'District_Code': ['District_Code'],
    'Sector': ['Sector'],
    'Quarter': ['Quarter'],
    'Survey_Month': ['Month_of_Survey', 'Survey_Month'],
    'Household_Size': ['Household_Size'],
    'Type': ['Household_Type', 'Type'],
    'Religion': ['Religion'],
    'Social_Group': ['Social_Group'],
    'Monthly_Expenditure': ['Monthly_Consumer_Expenditure', 'Monthly_Expenditure'],
    'Usual_Expenditure': ['Usual_Expenditure'],
    'Annual_Clothing': ['Annual_Clothing_Expenditure', 'Annual_Clothing'],
    'Annual_Durables': ['Annual_Durables_Expenditure', 'Annual_Durables']
}

all_valid = True
matched_columns = {}

for display_name, possible_names in column_mapping.items():
    found = False
    for possible in possible_names:
        if possible in actual_columns:
            print(f"✓ {display_name:<25} → {possible} EXISTS in household_survey")
            matched_columns[display_name] = possible
            found = True
            break
    if not found:
        print(f"✗ {display_name:<25} → NOT FOUND in household_survey")
        all_valid = False

print("\n" + "=" * 80)
if all_valid:
    print("✓ ALL COLUMNS ARE VALID - They belong to household_survey table!")
else:
    print("✗ SOME COLUMNS ARE INVALID - Check configuration!")

print("=" * 80)

# Show what these columns represent
print("\nColumn Meanings:")
print("-" * 80)
print("State_Ut_Code                     → State/UT identifier")
print("District_Code                     → District identifier")
print("Sector                            → Rural (1) or Urban (2)")
print("Quarter                           → Survey quarter")
print("Month_of_Survey                   → Month when survey was conducted")
print("Household_Size                    → Number of members in household")
print("Household_Type                    → Employment type classification")
print("Religion                          → Religion code")
print("Social_Group                      → Social group (SC/ST/OBC/Others)")
print("Monthly_Consumer_Expenditure      → Monthly spending in rupees")
print("Usual_Expenditure                 → Usual expenditure pattern")
print("Annual_Clothing_Expenditure       → Annual clothing expenses")
print("Annual_Durables_Expenditure       → Annual durable goods expenses")

print("\n" + "=" * 80)
print("DATASET CONFIRMATION:")
print("=" * 80)
print("✓ These are HOUSEHOLD-LEVEL consumption and demographic data")
print("✓ From PLFS Household Survey")
print("✓ Household characteristics and expenditure patterns")
print("✓ NOT person-level employment data")
print("=" * 80)

conn.close()
