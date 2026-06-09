"""
Create test users with plain passwords visible
"""
import httpx
import time

# Wait for server to start
print("Waiting for server to start...")
time.sleep(3)

base_url = "http://127.0.0.1:8889/api/v1"

# Test users to create
test_users = [
    {
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "password": "john123456",
        "role": "public"
    },
    {
        "username": "researcher1",
        "email": "researcher@example.com",
        "full_name": "Dr. Research",
        "password": "research123",
        "role": "researcher"
    },
    {
        "username": "premium_user",
        "email": "premium@example.com",
        "full_name": "Premium User",
        "password": "premium999",
        "role": "premium"
    }
]

print("="*60)
print("CREATING TEST USERS")
print("="*60)

for user_data in test_users:
    try:
        response = httpx.post(
            f"{base_url}/auth/register",
            json=user_data,
            timeout=10.0
        )
        
        if response.status_code == 201:
            user = response.json()
            print(f"\n✅ Created: {user_data['username']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Role: {user_data['role']}")
        else:
            print(f"\n❌ Failed to create {user_data['username']}: {response.text}")
    except Exception as e:
        print(f"\n❌ Error creating {user_data['username']}: {e}")

print("\n" + "="*60)
print("✅ Test users created! You can now:")
print("   1. Login as admin (username: admin, password: password)")
print("   2. View user management page")
print("   3. See all passwords in plain text!")
print("="*60)
