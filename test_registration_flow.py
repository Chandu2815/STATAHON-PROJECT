"""
Test script to verify user registration and login flow
"""
import httpx
import json

BASE_URL = "http://127.0.0.1:8888"

def test_registration():
    """Test user registration"""
    print("=" * 60)
    print("Testing User Registration Flow")
    print("=" * 60)
    
    # Test registration
    registration_data = {
        "email": "newuser@example.com",
        "username": "newuser123",
        "password": "securepass123",
        "full_name": "New Test User",
        "role": "public"
    }
    
    print("\n1. Registering new user...")
    print(f"   Username: {registration_data['username']}")
    print(f"   Email: {registration_data['email']}")
    print(f"   Role: {registration_data['role']}")
    
    response = httpx.post(
        f"{BASE_URL}/api/v1/auth/register",
        json=registration_data
    )
    
    if response.status_code == 201:
        user = response.json()
        print("\n   [SUCCESS] Registration successful!")
        print(f"   User ID: {user['id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['role']}")
        print(f"   Credits: {user['credits']}")
        print(f"   Active: {user['is_active']}")
    else:
        print(f"\n   [FAILED] Registration failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.json()}")
        return False
    
    # Test login
    print("\n2. Testing login with registered user...")
    login_data = {
        "username": registration_data["username"],
        "password": registration_data["password"]
    }
    
    response = httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        data=login_data
    )
    
    if response.status_code == 200:
        tokens = response.json()
        print("\n   [SUCCESS] Login successful!")
        print(f"   Token type: {tokens['token_type']}")
        print(f"   User role: {tokens['user_role']}")
        print(f"   Username: {tokens['username']}")
        print(f"   Access token: {tokens['access_token'][:50]}...")
        
        # Test authenticated request
        print("\n3. Testing authenticated API request...")
        headers = {
            "Authorization": f"Bearer {tokens['access_token']}"
        }
        
        response = httpx.get(
            f"{BASE_URL}/api/v1/users/me",
            headers=headers
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print("\n   [SUCCESS] Authenticated request successful!")
            print(f"   Username: {user_info['username']}")
            print(f"   Email: {user_info['email']}")
            print(f"   Credits: {user_info['credits']}")
        else:
            print(f"\n   [FAILED] Authenticated request failed!")
            print(f"   Status: {response.status_code}")
    else:
        print(f"\n   [FAILED] Login failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.json()}")
        return False
    
    print("\n" + "=" * 60)
    print("All tests passed! Registration system is working correctly!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_registration()
    except Exception as e:
        print(f"\n[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()
