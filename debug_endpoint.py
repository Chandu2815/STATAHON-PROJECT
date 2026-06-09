"""
Test by directly reading from database and simulating the endpoint logic
"""
import sqlite3
import json

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

# Simulate what the endpoint does
print("Simulating /plfs/district-codes?state=TELANGANA")
print("=" * 70)

# Get dataset 2 (district codes)
cursor.execute("SELECT id, name FROM datasets WHERE id = 2")
dataset = cursor.fetchone()
print(f"\nDataset: ID {dataset[0]}, Name: {dataset[1]}")

# Get all records for this dataset
cursor.execute("SELECT data FROM data_records WHERE dataset_id = 2 LIMIT 100")
records = cursor.fetchall()

# Convert to data format (what the endpoint does)
data = [json.loads(record[0]) for record in records]
total_count = len(records)

print(f"Total records fetched (with limit 100): {total_count}")

# Apply the filter (OLD WAY - BROKEN)
state = "TELANGANA"
old_filtered = [d for d in data if state.lower() in str(d.get('State', '')).lower()]
print(f"\nOLD filter (looking for 'State' field): {len(old_filtered)} records")

# Apply the filter (NEW WAY - SHOULD WORK)
new_filtered = [d for d in data if state.lower() in str(d.get('Unnamed: 1', '')).lower()]
print(f"NEW filter (looking for 'Unnamed: 1' field): {len(new_filtered)} records")

if new_filtered:
    print(f"\n✓ Filter IS working! Sample districts:")
    for i, record in enumerate(new_filtered[:3], 1):
        print(f"  {i}. {record.get('Unnamed: 3')} (State: {record.get('Unnamed: 1')})")
else:
    print("\n✗ Filter NOT working - checking data structure...")
    print("Sample record keys:")
    print(list(data[0].keys()))

# Now check ALL records (not just first 100)
cursor.execute("SELECT COUNT(*) FROM data_records WHERE dataset_id = 2")
total_all = cursor.fetchone()[0]
print(f"\n{'='*70}")
print(f"Note: Database has {total_all} total district records")

conn.close()
