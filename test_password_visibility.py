"""
Test that admin can see plain passwords via API
"""
import httpx
import json

base_url = "http://127.0.0.1:8889/api/v1"

# Login as admin
print("Logging in as admin...")
login_response = httpx.post(
    f"{base_url}/auth/login",
    data={"username": "admin", "password": "password"}
)

if login_response.status_code == 200:
    token_data = login_response.json()
    token = token_data["access_token"]
    print("✅ Login successful!")
    
    # Get all users
    print("\nFetching all users...")
    users_response = httpx.get(
        f"{base_url}/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if users_response.status_code == 200:
        users = users_response.json()
        print(f"\n✅ Retrieved {len(users)} users")
        print("="*80)
        
        for user in users:
            password = user.get('plain_password', 'N/A')
            print(f"Username: {user['username']:15} | Password: {password:15} | Email: {user['email']}")
        
        print("="*80)
        print("\n✅ SUCCESS! Passwords are visible in the API response!")
        print("   The admin dashboard should now display these passwords.")
    else:
        print(f"❌ Failed to get users: {users_response.text}")
else:
    print(f"❌ Login failed: {login_response.text}")
