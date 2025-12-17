"""
Simple test to verify the API is working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8080"

print("\n" + "="*60)
print("  Testing MoSPI Data Portal API")
print("="*60 + "\n")

# Test 1: Health Check
print("1. Health Check...")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}\n")

# Test 2: Root Endpoint
print("2. Root Endpoint...")
response = requests.get(f"{BASE_URL}/")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}\n")

# Test 3: OpenAPI Schema
print("3. OpenAPI Documentation Available...")
response = requests.get(f"{BASE_URL}/openapi.json")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    schema = response.json()
    print(f"   API Title: {schema.get('info', {}).get('title')}")
    print(f"   Version: {schema.get('info', {}).get('version')}")
    print(f"   Endpoints: {len(schema.get('paths', {}))}\n")

# Test 4: Get Pricing (No auth required)
print("4. Get Pricing Information...")
response = requests.get(f"{BASE_URL}/api/v1/users/pricing")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")

print("="*60)
print("✅ API Server is running and responding!")
print(f"📚 View full documentation at: {BASE_URL}/docs")
print("="*60 + "\n")
