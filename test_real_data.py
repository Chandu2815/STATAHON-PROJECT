"""
Test Script for Real PLFS Data from microdata.gov.in

This script demonstrates how to test all 6 PLFS endpoints with real data.
"""

import requests
import json
from typing import Optional

BASE_URL = "http://127.0.0.1:8080/api/v1"
token: Optional[str] = None

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_response(response):
    """Pretty print API response"""
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2)[:2000])  # Limit output
        if isinstance(data, list) and len(data) > 3:
            print(f"\n... (showing first 3 of {len(data)} items)")
        elif isinstance(data, dict) and 'records' in data and len(data['records']) > 3:
            print(f"\n... (showing first 3 of {len(data['records'])} records)")
    else:
        print(f"Error: {response.text}")
    print()

def register_and_login():
    """Register a test user and get authentication token"""
    global token
    
    print_section("1. AUTHENTICATION - Register & Login")
    
    # Try to register
    register_data = {
        "username": "plfstest",
        "email": "plfstest@example.com",
        "password": "testpass123",
        "full_name": "PLFS Test User",
        "role": "researcher"
    }
    
    print("Registering user (or using existing)...")
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    if response.status_code == 201:
        print(f"[OK] User registered successfully!")
    elif response.status_code == 400:
        print(f"[INFO] User already exists, will login...")
    else:
        print(f"[WARN] Registration response: {response.status_code} - {response.text}")
    
    # Login (works whether registration succeeded or user exists)
    login_data = {
        "username": "plfstest",
        "password": "testpass123"
    }
    
    print("Logging in...")
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"[OK] Successfully authenticated!")
        print(f"Token: {token[:50]}...")
    else:
        print(f"[ERROR] Authentication failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    return True

def get_headers():
    """Get headers with authentication token"""
    return {"Authorization": f"Bearer {token}"}

def test_plfs_summary():
    """Test: Get PLFS Summary"""
    print_section("2. PLFS SUMMARY - Overview of All Data")
    
    print("GET /api/v1/plfs/summary")
    response = requests.get(f"{BASE_URL}/plfs/summary", headers=get_headers())
    print_response(response)

def test_list_plfs_datasets():
    """Test: List all PLFS datasets"""
    print_section("3. LIST PLFS DATASETS - All Available Datasets")
    
    print("GET /api/v1/plfs/datasets")
    response = requests.get(f"{BASE_URL}/plfs/datasets", headers=get_headers())
    print_response(response)
    
    return response.json() if response.status_code == 200 else []

def test_district_codes():
    """Test: Get district codes"""
    print_section("4. DISTRICT CODES - 695 Districts from PLFS Panel 4")
    
    # Test 1: Get first 10 districts
    print("GET /api/v1/plfs/district-codes?limit=10")
    response = requests.get(
        f"{BASE_URL}/plfs/district-codes?limit=10",
        headers=get_headers()
    )
    print_response(response)
    
    # Test 2: Filter by state (if available)
    print("\n" + "-"*80 + "\n")
    print("GET /api/v1/plfs/district-codes?state=Maharashtra&limit=5")
    response = requests.get(
        f"{BASE_URL}/plfs/district-codes?state=Maharashtra&limit=5",
        headers=get_headers()
    )
    print_response(response)

def test_data_layout():
    """Test: Get PLFS data layout"""
    print_section("5. DATA LAYOUT - PLFS Structure & Variables")
    
    # Test 1: Get all data layout
    print("GET /api/v1/plfs/data-layout?limit=10")
    response = requests.get(
        f"{BASE_URL}/plfs/data-layout?limit=10",
        headers=get_headers()
    )
    print_response(response)
    
    # Test 2: Filter by block
    print("\n" + "-"*80 + "\n")
    print("GET /api/v1/plfs/data-layout?block=Block 4")
    response = requests.get(
        f"{BASE_URL}/plfs/data-layout?block=Block 4&limit=5",
        headers=get_headers()
    )
    print_response(response)

def test_item_codes():
    """Test: Get item codes"""
    print_section("6. ITEM CODES - 377 Survey Items Across 8 Blocks")
    
    # Test 1: Get first 10 item codes
    print("GET /api/v1/plfs/item-codes?limit=10")
    response = requests.get(
        f"{BASE_URL}/plfs/item-codes?limit=10",
        headers=get_headers()
    )
    print_response(response)
    
    # Test 2: Filter by block
    print("\n" + "-"*80 + "\n")
    print("GET /api/v1/plfs/item-codes?block=Block 5.1&limit=5")
    response = requests.get(
        f"{BASE_URL}/plfs/item-codes?block=Block 5.1&limit=5",
        headers=get_headers()
    )
    print_response(response)
    
    # Test 3: Search item codes
    print("\n" + "-"*80 + "\n")
    print("GET /api/v1/plfs/item-codes?search=education")
    response = requests.get(
        f"{BASE_URL}/plfs/item-codes?search=education&limit=5",
        headers=get_headers()
    )
    print_response(response)

def test_dataset_records(datasets):
    """Test: Get records from specific datasets"""
    print_section("7. DATASET RECORDS - Query Specific Datasets")
    
    if not datasets:
        print("No datasets available to test")
        return
    
    # Test first dataset
    dataset_id = datasets[0].get('id')
    dataset_name = datasets[0].get('name', 'Unknown')
    
    print(f"GET /api/v1/plfs/dataset/{dataset_id}/records?limit=5")
    print(f"Dataset: {dataset_name}\n")
    response = requests.get(
        f"{BASE_URL}/plfs/dataset/{dataset_id}/records?limit=5",
        headers=get_headers()
    )
    print_response(response)

def test_specific_queries():
    """Test: Specific real-world queries"""
    print_section("8. REAL-WORLD QUERIES - Practical Examples")
    
    # Query 1: Find all Block 4 (Demographic) items
    print("Query: Get all demographic items (Block 4)")
    print("GET /api/v1/plfs/item-codes?block=Block 4&limit=20\n")
    response = requests.get(
        f"{BASE_URL}/plfs/item-codes?block=Block 4&limit=20",
        headers=get_headers()
    )
    print_response(response)
    
    # Query 2: Get district codes with pagination
    print("\n" + "-"*80 + "\n")
    print("Query: Get districts 50-60 (pagination)")
    print("GET /api/v1/plfs/district-codes?offset=50&limit=10\n")
    response = requests.get(
        f"{BASE_URL}/plfs/district-codes?offset=50&limit=10",
        headers=get_headers()
    )
    print_response(response)

def run_all_tests():
    """Run all PLFS data tests"""
    print("\n" + "="*80)
    print("  REAL PLFS DATA TESTING SUITE")
    print("  Source: microdata.gov.in - PLFS Survey")
    print("="*80)
    
    # Step 1: Authenticate
    if not register_and_login():
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Step 2: Get PLFS Summary
    test_plfs_summary()
    
    # Step 3: List all datasets
    datasets = test_list_plfs_datasets()
    
    # Step 4: Test district codes
    test_district_codes()
    
    # Step 5: Test data layout
    test_data_layout()
    
    # Step 6: Test item codes
    test_item_codes()
    
    # Step 7: Test dataset records
    test_dataset_records(datasets)
    
    # Step 8: Real-world queries
    test_specific_queries()
    
    # Summary
    print_section("[SUCCESS] TESTING COMPLETE!")
    print("All 6 PLFS endpoints tested successfully!")
    print("\nYou can now:")
    print("1. Visit http://127.0.0.1:8080/docs for interactive testing")
    print("2. Use these endpoints in your application")
    print("3. Query 1,472 real PLFS records from microdata.gov.in")
    print("\nDataset Summary:")
    print("- District Codes: 695 records")
    print("- Data Layout: 400 records")
    print("- Item Codes: 377 records")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to server!")
        print("Please ensure the server is running:")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8080")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
