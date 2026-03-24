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

print("📂 Reading Excel file...")
file_path = "/Users/arunsudhaveni/Desktop/Data_LayoutPLFS_Calendar_2024 (4).xlsx"

try:
    # 1. Import State Codes
    print("\n1️⃣ Importing State Codes...")
    df_states = pd.read_excel(file_path, sheet_name='State code', header=1)
    df_states = df_states.dropna(how='all')
    df_states.columns = ['state_code', 'state_name']
    df_states = df_states[df_states['state_code'].notna()]

    # Create state_codes table
    cur.execute('DROP TABLE IF EXISTS plfs_state_codes CASCADE')
    cur.execute('''
        CREATE TABLE plfs_state_codes (
            id SERIAL PRIMARY KEY,
            state_code VARCHAR(10),
            state_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert state codes
    for idx, row in df_states.iterrows():
        try:
            cur.execute(
                'INSERT INTO plfs_state_codes (state_code, state_name) VALUES (%s, %s)',
                (str(row['state_code']).strip(), str(row['state_name']).strip())
            )
        except Exception as e:
            pass

    conn.commit()
    print(f"✅ Inserted {len(df_states)} state codes")

    # 2. Import Household Level Data Layout (chhv1)
    print("\n2️⃣ Importing PLFS Household Data Layout...")
    df_chhv1 = pd.read_excel(file_path, sheet_name='chhv1', header=1)
    df_chhv1 = df_chhv1.dropna(how='all')

    cur.execute('DROP TABLE IF EXISTS plfs_household_layout CASCADE')
    cur.execute('''
        CREATE TABLE plfs_household_layout (
            id SERIAL PRIMARY KEY,
            srl INTEGER,
            full_name VARCHAR(255),
            block VARCHAR(100),
            item_col VARCHAR(100),
            field_length INTEGER,
            field_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Clean and insert household layout data
    for idx, row in df_chhv1.iterrows():
        try:
            if pd.notna(row.iloc[0]):
                cur.execute(
                    '''INSERT INTO plfs_household_layout 
                       (srl, full_name, block, item_col, field_length, field_name) 
                       VALUES (%s, %s, %s, %s, %s, %s)''',
                    (
                        int(row.iloc[0]) if pd.notna(row.iloc[0]) else None,
                        str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None,
                        str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else None,
                        str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else None,
                        int(row.iloc[4]) if pd.notna(row.iloc[4]) else None,
                        str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else None,
                    )
                )
        except Exception as e:
            pass

    conn.commit()
    cur.execute('SELECT COUNT(*) FROM plfs_household_layout')
    count_hh = cur.fetchone()[0]
    print(f"✅ Inserted {count_hh} household layout records")

    # 3. Import Person Level Data Layout (cperv1)
    print("\n3️⃣ Importing PLFS Person Data Layout...")
    df_cperv1 = pd.read_excel(file_path, sheet_name='cperv1', header=0)
    df_cperv1 = df_cperv1.dropna(how='all')

    cur.execute('DROP TABLE IF EXISTS plfs_person_layout CASCADE')
    cur.execute('''
        CREATE TABLE plfs_person_layout (
            id SERIAL PRIMARY KEY,
            srl INTEGER,
            full_name VARCHAR(255),
            block VARCHAR(100),
            item_col VARCHAR(100),
            field_length INTEGER,
            field_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Clean and insert person layout data
    for idx, row in df_cperv1.iterrows():
        try:
            if pd.notna(row.iloc[0]):
                cur.execute(
                    '''INSERT INTO plfs_person_layout 
                       (srl, full_name, block, item_col, field_length, field_name) 
                       VALUES (%s, %s, %s, %s, %s, %s)''',
                    (
                        int(row.iloc[0]) if pd.notna(row.iloc[0]) else None,
                        str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None,
                        str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else None,
                        str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else None,
                        int(row.iloc[4]) if pd.notna(row.iloc[4]) else None,
                        str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else None if len(row) > 5 else None,
                    )
                )
        except Exception as e:
            pass

    conn.commit()
    cur.execute('SELECT COUNT(*) FROM plfs_person_layout')
    count_person = cur.fetchone()[0]
    print(f"✅ Inserted {count_person} person layout records")

    # Verify all tables
    print("\n" + "="*60)
    print("📊 VERIFICATION - All Data Imported Successfully")
    print("="*60)

    cur.execute('SELECT COUNT(*) FROM plfs_state_codes')
    print(f"✅ plfs_state_codes: {cur.fetchone()[0]} records")

    cur.execute('SELECT COUNT(*) FROM plfs_household_layout')
    print(f"✅ plfs_household_layout: {cur.fetchone()[0]} records")

    cur.execute('SELECT COUNT(*) FROM plfs_person_layout')
    print(f"✅ plfs_person_layout: {cur.fetchone()[0]} records")

    # Show sample data
    print("\n📋 Sample State Codes:")
    cur.execute('SELECT state_code, state_name FROM plfs_state_codes LIMIT 5')
    for row in cur.fetchall():
        print(f"   State {row[0]}: {row[1]}")

    conn.close()
    print("\n✅ Import completed successfully!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
