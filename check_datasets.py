import sqlite3

# Connect to the database
conn = sqlite3.connect('data/mospi.db')
cursor = conn.cursor()

# Check if tables exist
print("=== Database Tables ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Table: {table_name}, Rows: {count}")

# Check if household_survey and person_survey tables exist
if any('household_survey' in t[0] for t in tables):
    print("\n=== household_survey columns ===")
    cursor.execute("PRAGMA table_info(household_survey)")
    cols = cursor.fetchall()
    print(f"Total columns: {len(cols)}")
    for col in cols[:5]:
        print(f"  {col[1]} ({col[2]})")
    if len(cols) > 5:
        print(f"  ... and {len(cols) - 5} more columns")

conn.close()
