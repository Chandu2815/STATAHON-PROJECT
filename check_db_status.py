import psycopg2

def check_database():
    try:
        conn = psycopg2.connect(
            host='187.127.138.4', port=5432,
            database='statahon_db', user='postgres', password='NewPassword123'
        )
        cursor = conn.cursor()

        # List tables from information_schema
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = [t[0] for t in cursor.fetchall()]
        print("📊 Database Tables:")
        for table in tables:
            print(f"  - {table}")

        print("\n📈 Record Counts:")

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
            cursor.execute("SELECT username, role FROM users LIMIT 50")
            users = cursor.fetchall()
            print("\n👤 Users:")
            for username, role in users:
                print(f"  - {username} ({role})")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Database error: {e}")


if __name__ == "__main__":
    check_database()