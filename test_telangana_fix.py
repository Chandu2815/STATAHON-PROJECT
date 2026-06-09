"""
Test the fixed district codes filtering
"""
import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

print("=" * 70)
print("Testing District Codes with Telangana Filter")
print("=" * 70)

# First, let's register and login to get a fresh token
print("\n1. Registering test user...")
try:
    register_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpass123",
        "role": "PUBLIC"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code in [200, 201]:
        print("✓ User registered")
    elif response.status_code == 400 and "already registered" in response.text:
        print("✓ User already exists, will login")
    else:
        print(f"Registration response: {response.status_code}")
except Exception as e:
    print(f"Note: {e}")

print("\n2. Logging in...")
try:
    login_data = {
        "username": "testuser2",
        "password": "testpass123"
    }
    response = requests.post(
        f"{BASE_URL}/auth/login", 
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"✓ Logged in successfully")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test district codes with Telangana filter
        print("\n3. Testing /plfs/district-codes?state=TELANGANA...")
        response = requests.get(
            f"{BASE_URL}/plfs/district-codes?state=TELANGANA&limit=1000",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ SUCCESS!")
            print(f"  Total records in dataset: {data['total_records']}")
            print(f"  Telangana districts returned: {data['returned_records']}")
            
            if data['returned_records'] > 0:
                print(f"\n  First 5 Telangana districts:")
                for i, record in enumerate(data['data'][:5], 1):
                    district_name = record.get('Unnamed: 3', 'Unknown')
                    district_code = record.get('Unnamed: 2', '?')
                    print(f"    {i}. {district_name} (Code: {district_code})")
            else:
                print("\n  ✗ ERROR: No districts returned!")
        else:
            print(f"\n✗ Error: {response.status_code}")
            print(response.text)
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
