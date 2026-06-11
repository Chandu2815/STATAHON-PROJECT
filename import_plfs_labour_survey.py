import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text, Float, String, Integer
from sqlalchemy.pool import NullPool
import psycopg2

# Database config
DB_NAME = "statahon_db"
DB_USER = "postgres"
DB_PASSWORD = "NewPassword123"
DB_HOST = "127.0.0.1"
DB_PORT = 5432

# File path
CSV_DIR = "/Users/arunsudhaveni/Desktop/Data in CSV/"
CSV_FILE = None

# Find the exact filename
for file in os.listdir(CSV_DIR):
    if 'plfs' in file.lower():
        CSV_FILE = os.path.join(CSV_DIR, file)
        break

if not CSV_FILE:
    print("❌ PLFS CSV file not found")
    sys.exit(1)

print(f"📂 Found PLFS file: {os.path.basename(CSV_FILE)}")

# Create engine
engine = create_engine(
    f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    poolclass=NullPool
)

try:
    # Connect to database
    with engine.connect() as conn:
        conn.autocommit = True
        
        print(f"📊 Starting PLFS Labour Survey data import...")
        print(f"📁 File size: {os.path.getsize(CSV_FILE) / (1024**3):.2f} GB")
        
        # Process CSV in chunks to handle large file
        chunk_size = 50000
        table_name = 'plfs_labour_survey'
        
        print(f"\n1️⃣  Reading CSV in chunks (chunk size: {chunk_size})...")
        
        total_rows = 0
        first_chunk = True
        
        for chunk_idx, df_chunk in enumerate(pd.read_csv(CSV_FILE, chunksize=chunk_size)):
            print(f"   Processing chunk {chunk_idx + 1}...")
            
            # Clean column names (replace spaces with underscores)
            df_chunk.columns = [col.replace(' ', '_').replace('-', '_') for col in df_chunk.columns]
            
            # Handle data type conversion
            for col in df_chunk.columns:
                # Try to convert to numeric
                try:
                    df_chunk[col] = pd.to_numeric(df_chunk[col], errors='ignore')
                except:
                    pass
            
            # For first chunk, create the table
            if first_chunk:
                print(f"2️⃣  Creating table '{table_name}'...")
                
                # Drop table if exists
                conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
                conn.commit()
                
                # Use pandas to create the table
                df_chunk.to_sql(
                    table_name,
                    engine,
                    if_exists='replace',
                    method='multi',
                    index=False,
                    chunksize=5000
                )
                
                print(f"   ✅ Table created with {len(df_chunk.columns)} columns")
                first_chunk = False
            else:
                # Append subsequent chunks
                df_chunk.to_sql(
                    table_name,
                    engine,
                    if_exists='append',
                    method='multi',
                    index=False,
                    chunksize=5000
                )
            
            total_rows += len(df_chunk)
            print(f"   ✅ Chunk {chunk_idx + 1} imported: {len(df_chunk)} rows (Total: {total_rows})")
        
        # Verify the import
        print(f"\n3️⃣  Verifying import...")
        result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()
        
        print(f"\n{'=' * 60}")
        print(f"✅ PLFS Labour Survey data imported successfully!")
        print(f"{'=' * 60}")
        print(f"📊 Table: {table_name}")
        print(f"📈 Total rows: {result:,}")
        print(f"📋 Total columns: {len(df_chunk.columns)}")
        print(f"✨ Data is ready for analysis in PLFS category")
        
except Exception as e:
    print(f"❌ Error during import: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    engine.dispose()
