#!/usr/bin/env python3
"""
Database Inspector - Check tables, schemas, and data
"""
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    database="survey_db",
    user="postgres",
    password="1234"
)

cursor = conn.cursor(cursor_factory=RealDictCursor)

print("=" * 80)
print("📊 DATABASE INSPECTION - SURVEY_DB")
print("=" * 80)

# List all tables
print("\n📋 TABLES IN DATABASE:")
print("-" * 80)
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public'
    ORDER BY table_name;
""")
tables = cursor.fetchall()
for table in tables:
    print(f"  • {table['table_name']}")

# For each table, show record count
print("\n📈 TABLE STATISTICS:")
print("-" * 80)
for table in tables:
    table_name = table['table_name']
    cursor.execute(f"SELECT COUNT(*) as count FROM \"{table_name}\";")
    count = cursor.fetchone()['count']
    
    # Get column info
    cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='{table_name}'
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    
    print(f"\n  Table: {table_name}")
    print(f"    Records: {count}")
    print(f"    Columns ({len(columns)}):")
    for col in columns:
        print(f"      - {col['column_name']}: {col['data_type']}")

print("\n" + "=" * 80)
print("✅ Database inspection complete!")
print("=" * 80)

conn.close()
