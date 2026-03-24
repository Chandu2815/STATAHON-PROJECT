#!/usr/bin/env python3
"""
Database optimization - Create indexes for faster queries
"""

import psycopg2
from datetime import datetime

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "survey_db",
    "user": "postgres",
    "password": "1234"
}

def create_indexes():
    """Create indexes on commonly used columns"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("\n" + "="*70)
        print("🔧 Database Optimization - Creating Indexes")
        print("="*70)
        
        # Indexes to create
        indexes = [
            {
                'name': 'idx_survey_data_state',
                'table': 'survey_data',
                'columns': 'State',
                'description': 'Survey Data - State column'
            },
            {
                'name': 'idx_survey_data_sector',
                'table': 'survey_data',
                'columns': 'Sector',
                'description': 'Survey Data - Sector column'
            },
            {
                'name': 'idx_hces_level_01_state',
                'table': 'hces_level_01',
                'columns': 'State',
                'description': 'HCES Level 01 - State column'
            },
            {
                'name': 'idx_hces_level_02_state',
                'table': 'hces_level_02',
                'columns': 'State',
                'description': 'HCES Level 02 - State column'
            },
            {
                'name': 'idx_plfs_district_state',
                'table': 'plfs_district_codes',
                'columns': 'state_code',
                'description': 'PLFS Districts - State code'
            },
            {
                'name': 'idx_plfs_item_block',
                'table': 'plfs_item_codes',
                'columns': 'block_name',
                'description': 'PLFS Item Codes - Block name'
            }
        ]
        
        created_count = 0
        for idx in indexes:
            try:
                # Check if index already exists
                cur.execute("""
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = %s
                """, (idx['name'],))
                
                if cur.fetchone():
                    print(f"⏭️  Skipped - {idx['description']} (already exists)")
                    continue
                
                # Create index
                table = idx['table']
                columns = idx['columns']
                create_sql = f'CREATE INDEX {idx["name"]} ON "{table}" ("{columns}")'
                cur.execute(create_sql)
                conn.commit()
                created_count += 1
                print(f"✅ Created - {idx['description']}")
            except Exception as e:
                print(f"❌ Failed - {idx['description']}: {str(e)}")
                conn.rollback()
        
        # Analyze tables for query optimization
        print("\n📊 Analyzing tables for query optimization...")
        tables = ['survey_data', 'hces_level_01', 'hces_level_02', 'plfs_district_codes', 'plfs_item_codes']
        
        for table in tables:
            try:
                cur.execute(f'ANALYZE "{table}"')
                conn.commit()
                print(f"✅ Analyzed table: {table}")
            except Exception as e:
                print(f"⚠️  Could not analyze {table}: {str(e)}")
        
        print("\n" + "="*70)
        print(f"✅ Optimization Complete - {created_count} indexes created")
        print("="*70 + "\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Database connection error: {e}\n")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(create_indexes())
