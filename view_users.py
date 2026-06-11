#!/usr/bin/env python3
"""
View Users from Database
"""
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    # Database connection
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="statahon_db",
        user="postgres",
        password="NewPassword123"
    )

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    print("\n" + "=" * 100)
    print("👥 USERS IN DATABASE")
    print("=" * 100)

    # Query users
    cursor.execute("""
        SELECT id, username, email, full_name, role, credits, is_active, created_at 
        FROM "user" 
        ORDER BY created_at DESC;
    """)
    
    users = cursor.fetchall()
    
    if not users:
        print("\n⚠️  No users found in database\n")
    else:
        print(f"\n📊 Total Users: {len(users)}\n")
        
        for i, user in enumerate(users, 1):
            print(f"\n{i}. User ID: {user['id']}")
            print(f"   Username: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   Full Name: {user['full_name']}")
            print(f"   Role: {user['role']}")
            print(f"   Credits: {user['credits']}")
            print(f"   Active: {'✓ Yes' if user['is_active'] else '✗ No'}")
            print(f"   Created: {user['created_at']}")
            print("   " + "-" * 96)

    print("\n" + "=" * 100)

    conn.close()

except Exception as e:
    print(f"\n❌ Error: {e}\n")
