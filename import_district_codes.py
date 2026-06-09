#!/usr/bin/env python3
import pandas as pd
import psycopg2
from psycopg2 import sql

# Database connection
conn = psycopg2.connect(
    database="survey_db",
    user="postgres",
    password="1234",
    host="127.0.0.1",
    port=5432
)
cur = conn.cursor()

print("📂 Reading District Codes Excel file...")
file_path = "/Users/arunsudhaveni/Desktop/District_codes_PLFS_Panel_4_202324_2024 (1).xlsx"

try:
    # Read the sheet - skip first 2 rows of metadata
    df = pd.read_excel(file_path, sheet_name='2021-22-23', skiprows=2)
    
    print("\n📋 Data Preview:")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst 3 rows:")
    print(df.head(3))
    
    # Rename columns based on actual header
    if 'State Code' in df.columns:
        df.columns = ['state_code', 'state_name', 'district_code', 'district_name']
    else:
        # If columns are unnamed, rename by position
        df = df.iloc[1:]  # Skip the header row
        df.columns = ['state_code', 'state_name', 'district_code', 'district_name']
    
    # Remove rows with NaN values
    df = df.dropna()
    df = df[df['state_code'].notna()]
    
    print(f"\n✅ Cleaned data: {len(df)} rows")
    
    # Create district codes table
    print("\n1️⃣ Creating district_codes table...")
    cur.execute('DROP TABLE IF EXISTS plfs_district_codes CASCADE')
    cur.execute('''
        CREATE TABLE plfs_district_codes (
            id SERIAL PRIMARY KEY,
            state_code VARCHAR(10),
            state_name VARCHAR(100),
            district_code VARCHAR(10),
            district_name VARCHAR(150),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert district codes with proper error handling
    print("2️⃣ Inserting district codes...")
    success_count = 0
    error_count = 0
    
    for idx, row in df.iterrows():
        try:
            # Only insert rows with required data
            if pd.notna(row['state_code']) and pd.notna(row['state_name']) and pd.notna(row['district_code']) and pd.notna(row['district_name']):
                cur.execute(
                    '''INSERT INTO plfs_district_codes 
                       (state_code, state_name, district_code, district_name) 
                       VALUES (%s, %s, %s, %s)''',
                    (
                        str(row['state_code']).strip(),
                        str(row['state_name']).strip(),
                        str(row['district_code']).strip(),
                        str(row['district_name']).strip(),
                    )
                )
                success_count += 1
        except Exception as e:
            error_count += 1
            conn.rollback()  # Rollback failed transaction
            cur.execute('BEGIN')  # Start new transaction
    
    conn.commit()
    print(f"✅ Successfully inserted: {success_count} records")
    if error_count > 0:
        print(f"⚠️ Errors encountered: {error_count} records skipped")
    
    # Verify
    print("\n" + "="*60)
    print("📊 VERIFICATION - Import Complete")
    print("="*60)
    
    cur.execute('SELECT COUNT(*) FROM plfs_district_codes')
    total_count = cur.fetchone()[0]
    print(f"✅ Total records: {total_count}")
    
    cur.execute('SELECT DISTINCT state_code, state_name FROM plfs_district_codes ORDER BY state_code LIMIT 10')
    print(f"\n📍 Sample States:")
    for row in cur.fetchall():
        cur.execute('SELECT COUNT(*) FROM plfs_district_codes WHERE state_code = %s', (row[0],))
        count = cur.fetchone()[0]
        print(f"   {row[0]} - {row[1]}: {count} districts")
    
    print(f"\n📍 Sample Districts:")
    cur.execute('SELECT state_name, district_code, district_name FROM plfs_district_codes LIMIT 5')
    for row in cur.fetchall():
        print(f"   {row[0]} - District {row[1]}: {row[2]}")
    
    conn.close()
    print("\n✅ Import completed successfully!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
