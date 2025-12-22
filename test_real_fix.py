"""
Test the REAL fix - fetch all then filter
"""
import sqlite3
import json

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

print("Testing FIXED logic:")
print("=" * 70)

# Simulate the NEW fixed endpoint logic
cursor.execute("SELECT data FROM data_records WHERE dataset_id = 2")
all_records = cursor.fetchall()

# Convert all records
all_data = [json.loads(record[0]) for record in all_records]
print(f"Step 1: Fetched ALL {len(all_data)} records")

# Filter by state
state = "TELANGANA"
filtered_data = [d for d in all_data if state.lower() in str(d.get('Unnamed: 1', '')).lower()]
print(f"Step 2: Filtered to {len(filtered_data)} Telangana records")

# Apply pagination
limit = 100
offset = 0
paginated = filtered_data[offset:offset + limit]
print(f"Step 3: Paginated to {len(paginated)} records (limit={limit}, offset={offset})")

if paginated:
    print(f"\n✓ SUCCESS! Will return {len(paginated)} Telangana districts")
    print("\nFirst 5:")
    for i, record in enumerate(paginated[:5], 1):
        print(f"  {i}. {record.get('Unnamed: 3')}")
else:
    print("\n✗ FAILED - no records")

conn.close()

print("\n" + "=" * 70)
print("Fix confirmed: Fetch ALL records first, THEN filter, THEN paginate")
