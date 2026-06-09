import sqlite3
import json

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

# Get a sample record from district codes dataset (ID 2)
cursor.execute("SELECT data FROM data_records WHERE dataset_id = 2 LIMIT 5")
records = cursor.fetchall()

print("Sample district code records:")
print("=" * 70)
for i, record in enumerate(records, 1):
    data = json.loads(record[0])
    print(f"\nRecord {i}:")
    print(json.dumps(data, indent=2))
    
# Check if there are Telangana records
cursor.execute("SELECT data FROM data_records WHERE dataset_id = 2")
all_records = cursor.fetchall()

telangana_count = 0
for record in all_records:
    data = json.loads(record[0])
    # Check in the actual state name field
    if 'Unnamed: 1' in data and 'TELANGANA' in str(data['Unnamed: 1']).upper():
        telangana_count += 1
        if telangana_count <= 3:
            print(f"\nTelangana record {telangana_count}:")
            print(json.dumps(data, indent=2))

print(f"\n{'='*70}")
print(f"Total Telangana districts found: {telangana_count}")

conn.close()
