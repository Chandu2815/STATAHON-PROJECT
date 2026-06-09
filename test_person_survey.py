"""
Test person survey queries to verify dataset is working correctly
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_person_survey():
    """Test person survey queries"""
    
    # Login first to get token
    print("Logging in...")
    login_data = {
        "username": "chandu",
        "password": "test123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Login successful")
    
    # Test 1: Query person survey with filters
    print("\n" + "="*80)
    print("Test 1: Person Survey - TELANGANA, MALE, Age 20-30")
    print("="*80)
    
    query_params = {
        "dataset": 2,
        "state": "TELANGANA",
        "sector": "1",  # Rural
        "gender": "1",  # Male
        "min_age": 20,
        "max_age": 30
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/query", params=query_params, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Records found: {len(data)}")
        
        if len(data) > 0:
            print("\nFirst record:")
            first_record = data[0]
            # Print key fields
            important_fields = [
                'State_UT_Code', 'District_Code', 'Sector', 'Sex', 'Age',
                'Marital_Status', 'General_Education_Level', 'Principal_Status_Code',
                'CWS_Earnings_Salaried', 'CWS_Earnings_SelfEmployed'
            ]
            for field in important_fields:
                if field in first_record:
                    print(f"  {field}: {first_record[field]}")
            
            print("\nSample of 5 records:")
            for i, record in enumerate(data[:5], 1):
                print(f"  Record {i}: Age={record.get('Age')}, Sex={record.get('Sex')}, "
                      f"Education={record.get('General_Education_Level')}, "
                      f"Status={record.get('Principal_Status_Code')}")
    else:
        print(f"Query failed: {response.text}")
    
    # Test 2: Query with different filters
    print("\n" + "="*80)
    print("Test 2: Person Survey - KARNATAKA, FEMALE, Age 25-35, Urban")
    print("="*80)
    
    query_params = {
        "dataset": 2,
        "state": "KARNATAKA",
        "sector": "2",  # Urban
        "gender": "2",  # Female
        "min_age": 25,
        "max_age": 35
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/query", params=query_params, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Records found: {len(data)}")
        
        if len(data) > 0:
            print("\nAge distribution:")
            age_counts = {}
            for record in data:
                age = record.get('Age')
                age_counts[age] = age_counts.get(age, 0) + 1
            
            for age in sorted(age_counts.keys())[:10]:
                print(f"  Age {age}: {age_counts[age]} records")
    else:
        print(f"Query failed: {response.text}")
    
    # Test 3: Query household survey to compare
    print("\n" + "="*80)
    print("Test 3: Household Survey - TELANGANA, Rural (for comparison)")
    print("="*80)
    
    query_params = {
        "dataset": 1,
        "state": "TELANGANA",
        "sector": "1"  # Rural
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/query", params=query_params, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Records found: {len(data)}")
        
        if len(data) > 0:
            print("\nFirst household:")
            first_record = data[0]
            household_fields = [
                'State_Ut_Code', 'District_Code', 'Sector', 'Household_Size',
                'Monthly_Consumer_Expenditure', 'Religion', 'Social_Group'
            ]
            for field in household_fields:
                if field in first_record:
                    print(f"  {field}: {first_record[field]}")
    else:
        print(f"Query failed: {response.text}")

if __name__ == "__main__":
    test_person_survey()
