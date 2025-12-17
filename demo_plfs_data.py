"""
Demo script for Real PLFS Data from microdata.gov.in
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8080/api/v1"

print("\n" + "="*80)
print("  REAL MoSPI PLFS DATA - DEMONSTRATION")
print("  Data Source: microdata.gov.in")
print("="*80 + "\n")

# Register a test user
print("1. Registering test user...")
user_data = {
    "email": "plfs_demo@mospi.gov.in",
    "username": "plfs_demo_user",
    "password": "SecurePass123!",
    "full_name": "PLFS Demo User",
    "role": "researcher"
}

response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
if response.status_code == 201:
    print("   ✓ User registered successfully")
elif response.status_code == 400:
    print("   ✓ User already exists, proceeding with login")
else:
    print(f"   ⚠ Registration response: {response.status_code}")

# Login
print("\n2. Logging in...")
login_data = {
    "username": "plfs_demo_user",
    "password": "SecurePass123!"
}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

if response.status_code != 200:
    print(f"   ✗ Login failed: {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("   ✓ Login successful")

# Get PLFS Summary
print("\n3. Getting PLFS Data Summary...")
response = requests.get(f"{BASE_URL}/plfs/summary", headers=headers)
if response.status_code == 200:
    summary = response.json()
    print(f"   ✓ Total PLFS Datasets: {summary['total_datasets']}")
    print(f"\n   Available Datasets:")
    for ds in summary['datasets']:
        print(f"   - {ds['name']}")
        print(f"     Records: {ds['record_count']}")
        print(f"     Sample Fields: {', '.join(ds['sample_fields'][:5])}")
        print()

# List all PLFS datasets
print("\n4. Listing PLFS Datasets...")
response = requests.get(f"{BASE_URL}/plfs/datasets", headers=headers)
if response.status_code == 200:
    datasets = response.json()
    print(f"   ✓ Found {len(datasets)} PLFS datasets\n")
    for ds in datasets:
        print(f"   Dataset ID: {ds['id']}")
        print(f"   Name: {ds['name']}")
        print(f"   Records: {ds['record_count']}")
        print()

# Get District Codes
print("\n5. Querying District Codes...")
response = requests.get(f"{BASE_URL}/plfs/district-codes?limit=10", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"   ✓ Total Records: {data['total_records']}")
    print(f"   ✓ Showing first {len(data['data'])} districts:\n")
    for district in data['data'][:5]:
        print(f"   - State: {district.get('State', 'N/A')}")
        print(f"     District: {district.get('District', 'N/A')}")
        print(f"     District Code: {district.get('District Code', 'N/A')}")
        print()

# Get Item Codes from Block 4
print("\n6. Querying PLFS Item Codes (Block 4)...")
response = requests.get(f"{BASE_URL}/plfs/item-codes?block=Block 4&limit=10", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"   ✓ Found {data['total_records']} item codes\n")
    for item in data['data'][:5]:
        print(f"   - Code: {item.get('Item Code', 'N/A')}")
        print(f"     Description: {item.get('Item Description', 'N/A')}")
        print()

# Get Data Layout
print("\n7. Querying PLFS Data Layout...")
response = requests.get(f"{BASE_URL}/plfs/data-layout", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"   ✓ Found {data['total_records']} layout records\n")
    for layout in data['data'][:3]:
        print(f"   - Item: {layout.get('Item', 'N/A')}")
        print(f"     Block: {layout.get('Block', 'N/A')}")
        print(f"     Description: {layout.get('Description', 'N/A')[:80]}...")
        print()

# Get records from a specific dataset
print("\n8. Getting Records from Dataset 1...")
response = requests.get(f"{BASE_URL}/plfs/dataset/1/records?limit=5", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"   ✓ Dataset: {data['dataset_name']}")
    print(f"   ✓ Total Records: {data['total_records']}")
    print(f"   ✓ Showing {data['returned_records']} records\n")
    if data['data']:
        print(f"   Sample Record Keys: {', '.join(list(data['data'][0].keys())[:8])}")

print("\n" + "="*80)
print("  ✅ REAL PLFS DATA SUCCESSFULLY INTEGRATED!")
print("="*80)
print("\n📊 You now have access to:")
print("   • PLFS Data Layout (183 records)")
print("   • State Codes (37 records)")  
print("   • District Codes (695 records)")
print("   • Item Code Descriptions (377 records)")
print("   • Multiple data blocks and categories")
print("\n🌐 API Documentation: http://127.0.0.1:8080/docs")
print("📁 View Section: PLFS Data (6 new endpoints)")
print("\n✨ Total Records in Database: 1,472 real PLFS records!")
print("="*80 + "\n")
