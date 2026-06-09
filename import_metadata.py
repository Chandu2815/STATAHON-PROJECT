#!/usr/bin/env python3
import json
import psycopg2
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    database="survey_db",
    user="postgres",
    password="1234",
    host="127.0.0.1",
    port=5432
)
cur = conn.cursor()

print("📂 Reading NMDS Metadata JSON file...")
file_path = "data/mospi_real_data/NMDS_2.0_PLFS_final upd (1)_metadata.json"

try:
    # Read JSON file
    with open(file_path, 'r') as f:
        metadata = json.load(f)
    
    print(f"✅ File loaded successfully")
    print(f"Metadata keys: {list(metadata.keys())}")
    
    # Create metadata table
    print("\n1️⃣ Creating nmds_metadata table...")
    cur.execute('DROP TABLE IF EXISTS nmds_metadata CASCADE')
    cur.execute('''
        CREATE TABLE nmds_metadata (
            id SERIAL PRIMARY KEY,
            metadata_key VARCHAR(255),
            metadata_value TEXT,
            value_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert metadata
    print("2️⃣ Inserting metadata records...")
    success_count = 0
    
    for key, value in metadata.items():
        try:
            # Determine value type
            if isinstance(value, dict):
                value_type = 'object'
                value_str = json.dumps(value)
            elif isinstance(value, list):
                value_type = 'array'
                value_str = json.dumps(value) if len(str(value)) < 1000 else f"[{len(value)} items]"
            elif isinstance(value, bool):
                value_type = 'boolean'
                value_str = str(value)
            elif isinstance(value, (int, float)):
                value_type = 'number'
                value_str = str(value)
            else:
                value_type = 'string'
                value_str = str(value)[:1000]  # Limit string length
            
            cur.execute(
                '''INSERT INTO nmds_metadata 
                   (metadata_key, metadata_value, value_type) 
                   VALUES (%s, %s, %s)''',
                (str(key), value_str, value_type)
            )
            success_count += 1
        except Exception as e:
            conn.rollback()
            cur.execute('BEGIN')
            print(f"Error on key '{key}': {e}")
    
    conn.commit()
    print(f"\n✅ Inserted {success_count} metadata records")
    
    # Create a metadata summary table
    print("\n3️⃣ Creating metadata_summary table...")
    cur.execute('DROP TABLE IF EXISTS metadata_summary CASCADE')
    cur.execute('''
        CREATE TABLE metadata_summary (
            id SERIAL PRIMARY KEY,
            source_file VARCHAR(255),
            total_fields INTEGER,
            import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT
        )
    ''')
    
    cur.execute(
        '''INSERT INTO metadata_summary 
           (source_file, total_fields, description) 
           VALUES (%s, %s, %s)''',
        ('NMDS_2.0_PLFS_final upd (1).json', success_count, 'NMDS metadata import')
    )
    conn.commit()
    
    # Verify
    print("\n" + "="*60)
    print("📊 VERIFICATION - Metadata Import")
    print("="*60)
    
    cur.execute('SELECT COUNT(*) FROM nmds_metadata')
    count = cur.fetchone()[0]
    print(f"✅ Total metadata records: {count}")
    
    cur.execute('SELECT metadata_key, value_type, metadata_value FROM nmds_metadata LIMIT 10')
    print(f"\n📍 Sample metadata:")
    for row in cur.fetchall():
        val = row[2][:50] + "..." if len(row[2]) > 50 else row[2]
        print(f"   {row[0]:<20} ({row[1]:<10}): {val}")
    
    conn.close()
    print("\n✅ Metadata import completed!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
