"""
Test login endpoint directly with httpx
"""
import httpx
import json

BASE_URL = "http://127.0.0.1:8889"

def test_login():
    print("=" * 60)
    print("Testing Admin Login via API")
    print("=" * 60)
    
    # Test with form data (OAuth2PasswordRequestForm)
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print(f"\nSending login request to: {BASE_URL}/api/v1/auth/login")
    print(f"Username: {login_data['username']}")
    print(f"Password: {login_data['password']}")
    
    try:
        response = httpx.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10.0
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        print(response.text)
        
        if response.status_code == 200:
            tokens = response.json()
            print("\n✅ LOGIN SUCCESSFUL!")
            print(f"Access Token: {tokens.get('access_token', 'N/A')[:50]}...")
            print(f"Token Type: {tokens.get('token_type', 'N/A')}")
            print(f"User Role: {tokens.get('user_role', 'N/A')}")
            print(f"Username: {tokens.get('username', 'N/A')}")
        else:
            print(f"\n❌ LOGIN FAILED!")
            print(f"Status Code: {response.status_code}")
            try:
                error = response.json()
                print(f"Error Detail: {error.get('detail', 'Unknown error')}")
            except:
                print(f"Error Text: {response.text}")
                
    except httpx.ConnectError:
        print(f"\n❌ Cannot connect to {BASE_URL}")
        print("Make sure the server is running!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login()
