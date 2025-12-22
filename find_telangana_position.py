"""
Find where Telangana records are
"""
import sqlite3
import json

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

# Get ALL records
cursor.execute("SELECT id, data FROM data_records WHERE dataset_id = 2")
all_records = cursor.fetchall()

print(f"Total district records: {len(all_records)}")
print("=" * 70)

# Find Telangana records
telangana_positions = []
for i, (record_id, data_str) in enumerate(all_records):
    data = json.loads(data_str)
    state_name = data.get('Unnamed: 1', '')
    if 'TELANGANA' in state_name.upper():
        telangana_positions.append((i, record_id, data.get('Unnamed: 3', 'Unknown')))

print(f"\nFound {len(telangana_positions)} Telangana records")
print(f"\nPosition of Telangana records in dataset:")
print(f"  First Telangana record at position: {telangana_positions[0][0]} (record ID: {telangana_positions[0][1]})")
print(f"  Last Telangana record at position: {telangana_positions[-1][0]} (record ID: {telangana_positions[-1][1]})")

print(f"\nFirst 3 Telangana districts:")
for pos, rec_id, name in telangana_positions[:3]:
    print(f"  Position {pos}: {name}")

print(f"\n{'='*70}")
print("PROBLEM IDENTIFIED:")
print(f"The API is using limit=100 and offset=0 by default")
print(f"Telangana records start at position {telangana_positions[0][0]}")
print(f"So with limit=100, Telangana records are NOT fetched!")

conn.close()
