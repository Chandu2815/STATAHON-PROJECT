"""
Demo script to test the MoSPI Data Portal API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8080/api/v1"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(response):
    """Print formatted JSON response"""
    if response.status_code >= 200 and response.status_code < 300:
        print(f"✓ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"✗ Status: {response.status_code}")
        print(response.text)

# Test 1: Health Check
print_section("1. Health Check")
response = requests.get("http://127.0.0.1:8080/health")
print_response(response)

# Test 2: Register User
print_section("2. Register New User")
user_data = {
    "email": "researcher@university.edu",
    "username": "researcher01",
    "password": "SecurePass123!",
    "full_name": "Dr. Research Scholar",
    "role": "researcher"
}
response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
print_response(response)

# Test 3: Login
print_section("3. Login")
login_data = {
    "username": "researcher01",
    "password": "SecurePass123!"
}
response = requests.post(
    f"{BASE_URL}/auth/login",
    data=login_data
)
print_response(response)

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 4: Get Current User Info
    print_section("4. Get Current User Info")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response(response)
    
    # Test 5: Query Census Data - Female population in Maharashtra, age 15-29
    print_section("5. Query: Female in Maharashtra, Age 15-29")
    params = {
        "dataset": "census",
        "state": "Maharashtra",
        "gender": "Female",
        "age_group": "15-29"
    }
    response = requests.get(f"{BASE_URL}/query", params=params, headers=headers)
    print_response(response)
    
    # Test 6: Query with Ordering
    print_section("6. Query: Karnataka, Ordered by Population")
    params = {
        "dataset": "census",
        "state": "Karnataka",
        "order_by": "population",
        "order_direction": "desc"
    }
    response = requests.get(f"{BASE_URL}/query", params=params, headers=headers)
    print_response(response)
    
    # Test 7: Get Usage Statistics
    print_section("7. Get My Usage Statistics")
    response = requests.get(f"{BASE_URL}/users/me/usage", headers=headers)
    print_response(response)
    
    # Test 8: List Datasets
    print_section("8. List All Datasets")
    response = requests.get(f"{BASE_URL}/datasets", headers=headers)
    print_response(response)
    
    # Test 9: Get Pricing Info
    print_section("9. Get Pricing Information")
    response = requests.get(f"{BASE_URL}/users/pricing")
    print_response(response)
    
    print_section("Demo Complete!")
    print("\n📊 MoSPI Data Portal is working successfully!")
    print("🌐 Access API Documentation: http://127.0.0.1:8080/docs")
    print("🔑 Your token:", token[:50] + "...")

else:
    print("\n❌ Login failed. Cannot proceed with authenticated tests.")
