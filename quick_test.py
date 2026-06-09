"""
Quick test with fresh authentication
"""
import requests

BASE_URL = "http://localhost:8080/api/v1"

# Login with existing user
username = "demouser"
password = "demo123"
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": username, "password": password}
)

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✓ Got token: {token[:20]}...")
    
    # Test the district codes endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/plfs/district-codes?state=TELANGANA&limit=1000",
        headers=headers
    )
    
    print(f"\nAPI Response Status: {response.status_code}")
    data = response.json()
    print(f"Total records: {data['total_records']}")
    print(f"Returned records: {data['returned_records']}")
    
    if data['returned_records'] > 0:
        print(f"\n✓ SUCCESS! Found {data['returned_records']} Telangana districts")
        print("\nFirst 5 districts:")
        for i, record in enumerate(data['data'][:5], 1):
            print(f"  {i}. {record.get('Unnamed: 3', 'Unknown')}")
    else:
        print("\n✗ STILL BROKEN - returned 0 records")
        print("\nDebugging - First record in response:")
        if data.get('data'):
            print(data['data'][0])
else:
    print(f"Login failed: {response.status_code}")
    print(response.text)
