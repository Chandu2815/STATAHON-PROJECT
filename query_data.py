"""
Easy Data Query Tool - Filter Real PLFS Government Data
Simple interface to query 1,472 real records from microdata.gov.in
"""

import requests
import json
from typing import Optional

BASE_URL = "http://127.0.0.1:8080/api/v1"
token: Optional[str] = None

def login():
    """Quick login"""
    global token
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "tester", "password": "test1234"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return True
    return False

def get_headers():
    return {"Authorization": f"Bearer {token}"}

def show_menu():
    """Display menu"""
    print("\n" + "=" * 60)
    print("  PLFS DATA QUERY TOOL")
    print("  Quick access to 1,472 real government records")
    print("=" * 60)
    print("\n[1] View Summary - Overview of all data")
    print("[2] Search Districts - Query 695 district codes")
    print("[3] Search Item Codes - Query 377 survey items")
    print("[4] Filter by State - Get districts by state")
    print("[5] Filter by Block - Get items by block number")
    print("[6] Get Sample Data - See example records")
    print("[0] Exit")
    print("-" * 60)

def view_summary():
    """Show data summary"""
    print("\nFetching summary...")
    response = requests.get(f"{BASE_URL}/plfs/summary", headers=get_headers())
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + "=" * 60)
        print("  DATA SUMMARY")
        print("=" * 60)
        print(f"  Total Datasets: {data.get('total_datasets', 0)}")
        print(f"  Total Records: 1,472")
        print(f"\n  Available Data:")
        print(f"    • District Codes: 695 records")
        print(f"    • Item Codes: 377 records")
        print(f"    • Data Layout: 400 records")
        print(f"\n  Source: microdata.gov.in (PLFS Survey)")
        print("=" * 60)
    else:
        print(f"  Error: {response.status_code}")

def search_districts(limit=10):
    """Search district codes"""
    print(f"\nFetching first {limit} districts...")
    response = requests.get(
        f"{BASE_URL}/plfs/district-codes?limit={limit}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + "=" * 60)
        print(f"  DISTRICT CODES (showing {limit} of {data.get('total_records', 0)})")
        print("=" * 60)
        
        for i, record in enumerate(data.get('data', [])[:limit], 1):
            state = record.get('Unnamed: 1', 'N/A')
            district = record.get('Unnamed: 3', 'N/A')
            code = record.get('Unnamed: 2', 'N/A')
            print(f"  {i}. {district} ({state}) - Code: {code}")
        
        print(f"\n  Total available: {data.get('total_records', 0)} districts")
        print("=" * 60)
    else:
        print(f"  Error: {response.status_code}")

def search_item_codes(limit=10):
    """Search item codes"""
    print(f"\nFetching first {limit} item codes...")
    response = requests.get(
        f"{BASE_URL}/plfs/item-codes?limit={limit}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + "=" * 60)
        print(f"  ITEM CODES (showing {limit} of 377)")
        print("=" * 60)
        
        for i, record in enumerate(data.get('data', [])[:limit], 1):
            item = record.get('Unnamed: 1', 'N/A')
            code = record.get('Unnamed: 3', 'N/A')
            print(f"  {i}. {item} - Code: {code}")
        
        print(f"\n  Total available: 377 survey items")
        print("=" * 60)
    else:
        print(f"  Error: {response.status_code}")

def filter_by_state():
    """Filter districts by state"""
    print("\nEnter state name (e.g., PUNJAB, KERALA, MAHARASHTRA):")
    state = input("State: ").strip()
    
    if not state:
        print("  State name required!")
        return
    
    print(f"\nSearching for {state} districts...")
    response = requests.get(
        f"{BASE_URL}/plfs/district-codes?limit=100",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        # Filter by state name
        filtered = [r for r in data.get('data', []) 
                   if state.upper() in str(r.get('Unnamed: 1', '')).upper()]
        
        print("\n" + "=" * 60)
        print(f"  DISTRICTS IN {state.upper()}")
        print("=" * 60)
        
        if filtered:
            for i, record in enumerate(filtered, 1):
                district = record.get('Unnamed: 3', 'N/A')
                code = record.get('Unnamed: 2', 'N/A')
                print(f"  {i}. {district} - Code: {code}")
            print(f"\n  Total: {len(filtered)} districts found")
        else:
            print(f"  No districts found for '{state}'")
            print("  Try: PUNJAB, KERALA, MAHARASHTRA, TAMIL NADU, etc.")
        
        print("=" * 60)

def filter_by_block():
    """Filter items by block"""
    print("\nEnter block number (1-6):")
    block = input("Block: ").strip()
    
    if not block:
        print("  Block number required!")
        return
    
    print(f"\nSearching Block {block} items...")
    response = requests.get(
        f"{BASE_URL}/plfs/item-codes?limit=100",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        # Filter by block
        filtered = [r for r in data.get('data', []) 
                   if f"Block {block}" in str(r.get('sheet', ''))]
        
        print("\n" + "=" * 60)
        print(f"  BLOCK {block} ITEMS")
        print("=" * 60)
        
        if filtered:
            for i, record in enumerate(filtered[:20], 1):  # Show first 20
                item = record.get('Unnamed: 1', 'N/A')
                desc = record.get('Unnamed: 2', 'N/A')
                print(f"  {i}. {item}")
                if desc and desc != 'N/A':
                    print(f"     {desc}")
            
            if len(filtered) > 20:
                print(f"\n  ... and {len(filtered) - 20} more items")
            print(f"\n  Total: {len(filtered)} items in Block {block}")
        else:
            print(f"  No items found for Block {block}")
            print("  Available blocks: 1, 3, 4, 5.1, 5.2, 5.3, 6")
        
        print("=" * 60)

def get_sample_data():
    """Show sample data"""
    print("\n" + "=" * 60)
    print("  SAMPLE RECORDS")
    print("=" * 60)
    
    print("\n1. Sample Districts:")
    response = requests.get(
        f"{BASE_URL}/plfs/district-codes?limit=3",
        headers=get_headers()
    )
    if response.status_code == 200:
        data = response.json()
        for record in data.get('data', [])[:3]:
            print(f"   • {record.get('Unnamed: 3', 'N/A')} ({record.get('Unnamed: 1', 'N/A')})")
    
    print("\n2. Sample Item Codes:")
    response = requests.get(
        f"{BASE_URL}/plfs/item-codes?limit=3",
        headers=get_headers()
    )
    if response.status_code == 200:
        data = response.json()
        for record in data.get('data', [])[:3]:
            print(f"   • {record.get('Unnamed: 1', 'N/A')}")
    
    print("\n" + "=" * 60)

def main():
    """Main menu loop"""
    print("\n" + "=" * 60)
    print("  PLFS DATA QUERY TOOL")
    print("=" * 60)
    print("\nConnecting to server...")
    
    if not login():
        print("✗ Login failed. Make sure server is running:")
        print("  .\\start.ps1")
        return
    
    print("✓ Connected successfully!\n")
    
    while True:
        show_menu()
        choice = input("\nSelect option (0-6): ").strip()
        
        if choice == "0":
            print("\nExiting...\n")
            break
        elif choice == "1":
            view_summary()
        elif choice == "2":
            search_districts()
        elif choice == "3":
            search_item_codes()
        elif choice == "4":
            filter_by_state()
        elif choice == "5":
            filter_by_block()
        elif choice == "6":
            get_sample_data()
        else:
            print("\n  Invalid option. Please select 0-6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...\n")
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to server!")
        print("Start server with: .\\start.ps1\n")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
