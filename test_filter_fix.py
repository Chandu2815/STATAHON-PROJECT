#!/usr/bin/env python3
"""
Test script to verify the filter fix for household-level datasets
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def login():
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]

def test_query(token, dataset_id, filters, description):
    """Test a query with given filters"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"Dataset ID: {dataset_id}")
    print(f"Filters: {filters}")
    print(f"{'='*60}")
    
    params = {"dataset": dataset_id, "limit": 10}
    params.update(filters)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/query",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"   Total Records: {data.get('total_records', 'N/A')}")
        print(f"   Returned Records: {data.get('returned_records', 'N/A')}")
        print(f"   Filters Applied: {data.get('filters_applied', 'N/A')}")
        if data.get('skipped_filters'):
            print(f"   ⚠️  Skipped Filters: {data.get('skipped_filters')}")
            print(f"   📝 Note: {data.get('filter_notes', 'N/A')}")
        return data
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def main():
    print("🔐 Logging in...")
    token = login()
    print(f"✅ Got access token")
    
    # Test 1: Household Survey (ID: 1) with State only - should work
    test_query(token, 1, {"state": "TELANGANA"}, 
               "Household Survey with State filter (should work)")
    
    # Test 2: Household Survey (ID: 1) with Gender - should skip gender
    test_query(token, 1, {"state": "TELANGANA", "gender": "MALE"}, 
               "Household Survey with State + Gender (gender should be skipped)")
    
    # Test 3: Household Survey (ID: 1) with all filters - should skip gender & age
    test_query(token, 1, {"state": "TELANGANA", "gender": "MALE", "age_group": "15-29"}, 
               "Household Survey with State + Gender + Age (gender & age should be skipped)")
    
    # Test 4: Person Survey (ID: 2) with all filters - all should work
    test_query(token, 2, {"state": "TELANGANA", "gender": "MALE", "age_group": "15-29"}, 
               "Person Survey with State + Gender + Age (all should work)")
    
    # Test 5: Person Survey (ID: 2) with Gender only
    test_query(token, 2, {"gender": "FEMALE"}, 
               "Person Survey with Gender only (should work)")
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
