import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('mospi_dpi.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print("📊 Database Tables:")
        for table in tables:
            print(f"  - {table}")
        
        print("\n📈 Record Counts:")
        
        # Check each dataset
        datasets = ['users', 'household_survey', 'person_survey', 'hces_household_identification', 'hces_food_expenditure', 'hces_non_food_expenditure']
        
        for dataset in datasets:
            if dataset in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {dataset}")
                count = cursor.fetchone()[0]
                print(f"  {dataset}: {count:,} records")
            else:
                print(f"  {dataset}: ❌ Table not found")
        
        # Check users specifically
        if 'users' in tables:
            cursor.execute("SELECT username, role FROM users")
            users = cursor.fetchall()
            print("\n👤 Users:")
            for username, role in users:
                print(f"  - {username} ({role})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_database()