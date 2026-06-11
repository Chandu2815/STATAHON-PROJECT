#!/usr/bin/env python3
"""
Import HCES 2023-24 data from multiple CSV files into PostgreSQL
"""

import pandas as pd
import psycopg2
from datetime import datetime
import os

# Database connection parameters
DB_HOST = '127.0.0.1'
DB_PORT = 5432
DB_NAME = 'survey_db'
DB_USER = 'postgres'
DB_PASSWORD = 'NewPassword123'

# File mappings
CSV_FILES = [
    {
        'path': '/Users/arunsudhaveni/Desktop/HCES_Data_2023-24_Csv/LEVEL - 01(Section 1 and 1_1).csv',
        'table': 'hces_level_01',
        'description': 'HCES Level 01 - Section 1 and 1_1 Data'
    },
    {
        'path': '/Users/arunsudhaveni/Desktop/HCES_Data_2023-24_Csv/LEVEL - 02 (Section 3).csv',
        'table': 'hces_level_02',
        'description': 'HCES Level 02 - Section 3 Data'
    },
    {
        'path': '/Users/arunsudhaveni/Desktop/HCES_Data_2023-24_Csv/LEVEL - 03.csv',
        'table': 'hces_level_03',
        'description': 'HCES Level 03 Data'
    },
    {
        'path': '/Users/arunsudhaveni/Desktop/HCES_Data_2023-24_Csv/LEVEL - 04 (Section 4_1).csv',
        'table': 'hces_level_04',
        'description': 'HCES Level 04 - Section 4_1 Data'
    }
]

def sanitize_column_name(col_name):
    """Convert column name to valid SQL identifier"""
    # Replace spaces and special chars with underscores
    col_name = col_name.strip().lower()
    col_name = col_name.replace(' ', '_').replace('-', '_').replace('.', '_')
    # Remove multiple underscores
    while '__' in col_name:
        col_name = col_name.replace('__', '_')
    return col_name[:63]  # PostgreSQL identifier limit

def create_table(conn, cursor, table_name, columns):
    """Create table with appropriate data types"""
    try:
        # Build column definitions
        col_defs = []
        for col in columns:
            col_name = sanitize_column_name(col)
            # Try to determine if numeric
            col_defs.append(f'"{col_name}" TEXT')
        
        create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (id SERIAL PRIMARY KEY, {", ".join(col_defs)})'
        cursor.execute(create_sql)
        conn.commit()
        print(f"✅ Table '{table_name}' created/verified")
        return True
    except Exception as e:
        print(f"❌ Error creating table '{table_name}': {e}")
        conn.rollback()
        return False

def insert_data(conn, cursor, table_name, df):
    """Insert dataframe into table"""
    try:
        # Sanitize column names
        sanitized_columns = [sanitize_column_name(col) for col in df.columns]
        df.columns = sanitized_columns
        
        # Handle NaN/None values
        df = df.where(pd.notna(df), None)
        
        # Insert in batches
        batch_size = 500
        total_rows = len(df)
        inserted = 0
        
        # Create insert template
        col_names = ', '.join([f'"{col}"' for col in sanitized_columns])
        placeholders = ', '.join(['%s'] * len(sanitized_columns))
        insert_sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            records = [tuple(row) for row in batch_df.values]
            
            # Use executemany for batch insert
            cursor.executemany(insert_sql, records)
            
            inserted += len(records)
            print(f"  ⏳ Inserted {inserted}/{total_rows} rows...")
        
        conn.commit()
        print(f"✅ Successfully inserted {total_rows} rows into '{table_name}'")
        return total_rows
    except Exception as e:
        print(f"❌ Error inserting data into '{table_name}': {e}")
        conn.rollback()
        return 0

def main():
    print("\n" + "="*70)
    print("📊 HCES 2023-24 Data Import Script")
    print("="*70)
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        total_imported = 0
        successful_imports = 0
        
        for file_config in CSV_FILES:
            file_path = file_config['path']
            table_name = file_config['table']
            description = file_config['description']
            
            print(f"\n📂 Processing: {description}")
            print(f"📄 File: {os.path.basename(file_path)}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                continue
            
            try:
                # Read CSV file
                print(f"📥 Reading CSV file...")
                df = pd.read_csv(file_path)
                rows = len(df)
                cols = len(df.columns)
                
                print(f"✅ File loaded: {rows} rows × {cols} columns")
                print(f"   Columns: {', '.join(df.columns[:5])}{'...' if cols > 5 else ''}")
                
                # Create table
                if not create_table(conn, cursor, table_name, df.columns):
                    continue
                
                # Clear existing data (optional - uncomment to replace instead of append)
                # cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE')
                # conn.commit()
                
                # Insert data
                inserted = insert_data(conn, cursor, table_name, df)
                if inserted > 0:
                    total_imported += inserted
                    successful_imports += 1
                
            except Exception as e:
                print(f"❌ Error processing file: {e}")
                continue
        
        # Final summary
        print("\n" + "="*70)
        print("📊 Import Summary")
        print("="*70)
        print(f"✅ Successfully imported: {successful_imports}/{len(CSV_FILES)} files")
        print(f"📈 Total rows imported: {total_imported:,}")
        print("="*70 + "\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Database connection error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
