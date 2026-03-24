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

print("📂 Reading PLFS Item Codes Excel file...")
file_path = "data/mospi_real_data/PLFS Panel 4 Sch 10.4 Item Code Description & Codes (1).xlsx"

try:
    # Create item codes table
    print("\n1️⃣ Creating plfs_item_codes table...")
    cur.execute('DROP TABLE IF EXISTS plfs_item_codes CASCADE')
    cur.execute('''
        CREATE TABLE plfs_item_codes (
            id SERIAL PRIMARY KEY,
            block_name VARCHAR(100),
            item_number VARCHAR(50),
            item_description VARCHAR(500),
            code_value VARCHAR(50),
            code_description VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Read all sheets and import data
    xls = pd.ExcelFile(file_path)
    total_records = 0
    
    for sheet in xls.sheet_names:
        print(f"\n2️⃣ Processing sheet: '{sheet}'...")
        df = pd.read_excel(file_path, sheet_name=sheet, skiprows=1)
        
        # Clean data first
        df = df.dropna(how='all')
        
        # Handle different number of columns
        cols_to_use = list(df.columns)[:4]  # Use first 4 columns regardless of total
        df = df[cols_to_use]
        df.columns = ['item_number', 'item_description', 'code_value', 'code_description']
        
        # Remove rows where first column is NaN
        df = df[df['item_number'].notna()]
        
        # Insert records
        success_count = 0
        for idx, row in df.iterrows():
            try:
                if pd.notna(row['item_number']):
                    cur.execute(
                        '''INSERT INTO plfs_item_codes 
                           (block_name, item_number, item_description, code_value, code_description) 
                           VALUES (%s, %s, %s, %s, %s)''',
                        (
                            str(sheet).strip(),
                            str(row['item_number']).strip() if pd.notna(row['item_number']) else None,
                            str(row['item_description']).strip() if pd.notna(row['item_description']) else None,
                            str(row['code_value']).strip() if pd.notna(row['code_value']) else None,
                            str(row['code_description']).strip() if pd.notna(row['code_description']) else None,
                        )
                    )
                    success_count += 1
            except Exception as e:
                conn.rollback()
                cur.execute('BEGIN')
        
        conn.commit()
        print(f"   ✅ Sheet '{sheet}': {success_count} records")
        total_records += success_count
    
    # Verify
    print("\n" + "="*60)
    print("📊 VERIFICATION - Item Codes Import")
    print("="*60)
    
    cur.execute('SELECT COUNT(*) FROM plfs_item_codes')
    count = cur.fetchone()[0]
    print(f"✅ Total item codes: {count}")
    
    cur.execute('SELECT DISTINCT block_name FROM plfs_item_codes ORDER BY block_name')
    print(f"\n📍 Blocks:")
    for row in cur.fetchall():
        cur.execute('SELECT COUNT(*) FROM plfs_item_codes WHERE block_name = %s', (row[0],))
        b_count = cur.fetchone()[0]
        print(f"   {row[0]}: {b_count} items")
    
    conn.close()
    print("\n✅ Item codes import completed!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
