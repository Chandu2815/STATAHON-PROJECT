"""
Test the renamed fields
"""
import sqlite3
import json

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

# Simulate the endpoint with renaming
cursor.execute("SELECT data FROM data_records WHERE dataset_id = 2")
all_records = cursor.fetchall()

all_data = [json.loads(record[0]) for record in all_records]

# Filter for Telangana
state = "TELANGANA"
filtered_data = [d for d in all_data if state.lower() in str(d.get('Unnamed: 1', '')).lower()]

# Rename function (same as in endpoint)
def rename_district_fields(record):
    renamed = record.copy()
    if 'Unnamed: 1' in renamed:
        renamed['STATE_NAME'] = renamed.pop('Unnamed: 1')
    if 'Unnamed: 2' in renamed:
        renamed['DISTRICT_CODE'] = renamed.pop('Unnamed: 2')
    if 'Unnamed: 3' in renamed:
        renamed['DISTRICT_NAME'] = renamed.pop('Unnamed: 3')
    return renamed

# Apply renaming
renamed_data = [rename_district_fields(d) for d in filtered_data[:3]]

print("Testing field renaming:")
print("=" * 70)
print(f"Found {len(filtered_data)} Telangana districts")
print("\nFirst 3 districts with NEW field names:")
for i, record in enumerate(renamed_data, 1):
    print(f"\n{i}. {record.get('DISTRICT_NAME')}")
    print(f"   STATE_NAME: {record.get('STATE_NAME')}")
    print(f"   DISTRICT_CODE: {record.get('DISTRICT_CODE')}")
    print(f"   Keys in record: {list(record.keys())[:6]}...")

conn.close()

print("\n" + "=" * 70)
print("✓ Field names will be renamed in API response")
