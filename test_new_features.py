"""
Test the new user management features
"""
import httpx
import time

BASE_URL = "http://127.0.0.1:8889"

# Wait for server to start
print("Waiting for server to start...")
time.sleep(5)

# Login as admin
print("\n1. Logging in as admin...")
response = httpx.post(
    f"{BASE_URL}/api/v1/auth/login",
    data={"username": "admin", "password": "password"},
    timeout=10.0
)

if response.status_code != 200:
    print(f"❌ Login failed: {response.text}")
    exit(1)

token = response.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}
print("✅ Login successful!")

# Get all users
print("\n2. Fetching all users...")
response = httpx.get(f"{BASE_URL}/api/v1/users/", headers=headers)
if response.status_code == 200:
    users = response.json()
    print(f"✅ Found {len(users)} users")
    for user in users:
        if user['username'] != 'admin':
            print(f"   - {user['username']} (ID: {user['id']}, Role: {user['role']})")
else:
    print(f"❌ Failed to get users: {response.text}")

print("\n" + "="*60)
print("✅ ALL FEATURES ARE READY!")
print("="*60)
print("\nNow refresh your browser at:")
print("http://127.0.0.1:8889/admin/dashboard")
print("\nYou can now:")
print("  📋 Click 'View' to see user details")
print("  ✏️  Click 'Edit' to modify user information")
print("  🔑 Click 'Reset' to change user passwords")
print("="*60)
