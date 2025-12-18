"""
Test all datasets endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

# Get token (you'll need to use valid credentials)
print("=" * 70)
print("Testing Dataset Endpoints")
print("=" * 70)

# Test 1: List all available tables (no auth required)
print("\n1. Testing /datasets/tables (public endpoint)...")
try:
    response = requests.get(f"{BASE_URL}/datasets/tables")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {data['total_tables']} tables")
        for table in data['tables']:
            print(f"  - {table['table_name']}: {table['row_count']} rows")
    else:
        print(f"✗ Error: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# For authenticated endpoints, you need a valid token
print("\n" + "=" * 70)
print("For authenticated tests, you need to:")
print("1. Register: POST /api/v1/auth/register")
print("2. Login: POST /api/v1/auth/login")
print("3. Use the returned token in Authorization header")
print("=" * 70)

# Test endpoint availability
endpoints = [
    ("GET", "/datasets", "List all datasets"),
    ("GET", "/datasets/2/schema", "Schema for dataset 2 (district codes - data_records storage)"),
    ("GET", "/datasets/4/schema", "Schema for dataset 4 (household_survey - dedicated table)"),
    ("GET", "/datasets/5/schema", "Schema for dataset 5 (person_survey - dedicated table)"),
    ("GET", "/query/dataset/2/records?limit=5", "Query dataset 2 records"),
    ("GET", "/query/dataset/4/records?limit=5", "Query dataset 4 records"),
    ("GET", "/query/household_survey?limit=5", "Query household_survey table"),
    ("GET", "/query/person_survey?limit=5", "Query person_survey table"),
]

print("\nAvailable endpoints (require authentication):")
for method, endpoint, description in endpoints:
    print(f"  {method} {BASE_URL}{endpoint}")
    print(f"      → {description}")
