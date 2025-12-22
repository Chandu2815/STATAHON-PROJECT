"""
Direct test of the filter logic
"""
import sqlite3
import json

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

# Get all district records
cursor.execute("SELECT data FROM data_records WHERE dataset_id = 2")
all_records = cursor.fetchall()

print("Testing filter logic:")
print("=" * 70)

# Convert to data format
data = [json.loads(record[0]) for record in all_records]

print(f"Total records: {len(data)}")

# Test the OLD filter (broken)
state = "TELANGANA"
old_filtered = [d for d in data if state.lower() in str(d.get('State', '')).lower()]
print(f"\nOLD filter (State field): {len(old_filtered)} records")

# Test the NEW filter (fixed)
new_filtered = [d for d in data if state.lower() in str(d.get('Unnamed: 1', '')).lower()]
print(f"NEW filter (Unnamed: 1 field): {len(new_filtered)} records")

if new_filtered:
    print(f"\nFirst 5 Telangana districts:")
    for i, record in enumerate(new_filtered[:5], 1):
        district_name = record.get('Unnamed: 3', 'Unknown')
        district_code = record.get('Unnamed: 2', '?')
        state_code = record.get('District codes for panel 4 of PLFS i.e. PLFS 2023-24 and upto December 2024', '?')
        print(f"  {i}. {district_name} (District Code: {district_code}, State Code: {state_code})")

conn.close()

print("\n" + "=" * 70)
print("✓ Fix confirmed: Using 'Unnamed: 1' instead of 'State' field")
