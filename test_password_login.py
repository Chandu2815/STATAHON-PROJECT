"""
Test login with password "password"
"""
import httpx

BASE_URL = "http://127.0.0.1:8889"

login_data = {
    "username": "admin",
    "password": "password"
}

print(f"Attempting login at: {BASE_URL}/api/v1/auth/login")
print(f"Username: {login_data['username']}")
print(f"Password: {login_data['password']}")
print()

try:
    response = httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10.0
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print()
    
    if response.status_code == 200:
        tokens = response.json()
        print("✅ ✅ ✅ LOGIN SUCCESSFUL! ✅ ✅ ✅")
        print()
        print(f"Access Token: {tokens.get('access_token', 'N/A')[:60]}...")
        print(f"Token Type: {tokens.get('token_type', 'N/A')}")
        print(f"User Role: {tokens.get('user_role', 'N/A')}")
        print(f"Username: {tokens.get('username', 'N/A')}")
        print()
        print("=" * 60)
        print("NOW TRY IN BROWSER:")
        print("=" * 60)
        print(f"URL: {BASE_URL}/admin/login")
        print(f"Username: admin")
        print(f"Password: password")
        print("=" * 60)
    else:
        print("❌ LOGIN FAILED")
        print(f"Error: {response.text}")
        
except httpx.ConnectError:
    print(f"❌ Cannot connect to {BASE_URL}")
    print("Make sure server is running!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
