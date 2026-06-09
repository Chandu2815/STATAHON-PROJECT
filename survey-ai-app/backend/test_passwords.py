import psycopg2
import sys

host = "187.127.138.4"
port = 5432
dbname = "statahon_db"
user = "postgres"

passwords = [
    "Statathon2026",
    "Statathon@2026",
    "Statahon@123",
    "Statathon@123",
    "Statathon123",
    "Survey@123",
    "postgres",
    "admin"
]

print("Starting database credential test...")

for pwd in passwords:
    try:
        print(f"Trying password: {pwd[:3]}...{pwd[-3:] if len(pwd) > 3 else ''}")
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=pwd,
            connect_timeout=5
        )
        print(f"✅ SUCCESS! Correct password is: {pwd}")
        conn.close()
        sys.exit(0)
    except psycopg2.OperationalError as e:
        print(f"❌ Failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("None of the passwords worked.")
