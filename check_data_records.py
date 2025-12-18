import sqlite3

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

# Check data_records table
cursor.execute("SELECT dataset_id, COUNT(*) FROM data_records GROUP BY dataset_id")
records = cursor.fetchall()

print("Data in data_records table:")
for dataset_id, count in records:
    cursor.execute("SELECT name FROM datasets WHERE id = ?", (dataset_id,))
    name = cursor.fetchone()
    print(f"  Dataset {dataset_id} ({name[0] if name else 'Unknown'}): {count} records")

# Check actual PLFS tables
print("\nPLFS survey tables:")
cursor.execute("SELECT COUNT(*) FROM household_survey")
print(f"  household_survey: {cursor.fetchone()[0]} rows")

cursor.execute("SELECT COUNT(*) FROM person_survey")
print(f"  person_survey: {cursor.fetchone()[0]} rows")

conn.close()
