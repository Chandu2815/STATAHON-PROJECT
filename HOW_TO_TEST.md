# 🧪 How to Test Real PLFS Data

## Quick Start - Test via Swagger UI (Recommended)

### Step 1: Access Swagger Documentation
1. **Open your browser** and go to: http://127.0.0.1:8080/docs
2. You'll see the interactive API documentation

### Step 2: Register a User
1. Find the **"Authentication"** section
2. Click on **`POST /api/v1/auth/register`**
3. Click **"Try it out"**
4. Fill in the request body:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "full_name": "Test User",
  "role": "researcher"
}
```
5. Click **"Execute"**
6. You should see a `201 Created` response

### Step 3: Login
1. Find **`POST /api/v1/auth/login`**
2. Click **"Try it out"**
3. Enter credentials:
   - `username`: testuser
   - `password`: password123
4. Click **"Execute"**
5. **Copy the `access_token`** from the response

### Step 4: Authorize
1. Click the **"Authorize"** button at the top right
2. Enter: `Bearer <your_access_token>`
3. Click **"Authorize"**, then **"Close"**

### Step 5: Test PLFS Endpoints 🎉

Now you can test all 6 PLFS endpoints!

---

## 📊 Test 1: Get PLFS Summary
**Endpoint:** `GET /api/v1/plfs/summary`

1. Scroll to **"PLFS Data"** section
2. Click on **`GET /api/v1/plfs/summary`**
3. Click **"Try it out"** → **"Execute"**

**What you'll see:**
- Total PLFS datasets (3)
- Total records (1,472)
- Summary of district codes, data layout, and item codes

---

## 📂 Test 2: List All PLFS Datasets
**Endpoint:** `GET /api/v1/plfs/datasets`

1. Click on **`GET /api/v1/plfs/datasets`**
2. Click **"Try it out"** → **"Execute"**

**What you'll see:**
```json
[
  {
    "id": 1,
    "name": "PLFS Data Layout 2024",
    "record_count": 400,
    "source": "microdata.gov.in"
  },
  {
    "id": 2,
    "name": "District Codes PLFS Panel 4 (2023-24)",
    "record_count": 695,
    "source": "microdata.gov.in"
  },
  {
    "id": 3,
    "name": "PLFS Item Codes Schedule 10.4",
    "record_count": 377,
    "source": "microdata.gov.in"
  }
]
```

---

## 🗺️ Test 3: Get District Codes
**Endpoint:** `GET /api/v1/plfs/district-codes`

### Get First 10 Districts:
1. Click on **`GET /api/v1/plfs/district-codes`**
2. Click **"Try it out"**
3. Set `limit`: 10
4. Click **"Execute"**

**Sample Response:**
```json
{
  "total": 695,
  "records": [
    {
      "district_code": "101",
      "district_name": "Kupwara",
      "state_code": "01",
      "state_name": "Jammu & Kashmir"
    },
    ...
  ]
}
```

### Filter by State:
1. Set `state`: Maharashtra
2. Set `limit`: 20
3. Click **"Execute"**

You'll get all Maharashtra districts!

---

## 📋 Test 4: Get Data Layout
**Endpoint:** `GET /api/v1/plfs/data-layout`

1. Click on **`GET /api/v1/plfs/data-layout`**
2. Click **"Try it out"**
3. Set `limit`: 20
4. Click **"Execute"**

**What it shows:**
- Item numbers
- Item descriptions
- Data types
- Variable names
- Sheet information

### Filter by Block:
1. Set `block`: Block 4
2. Click **"Execute"**

Gets only demographic particulars!

---

## 🔢 Test 5: Get Item Codes
**Endpoint:** `GET /api/v1/plfs/item-codes`

### Get All Blocks:
1. Click on **`GET /api/v1/plfs/item-codes`**
2. Click **"Try it out"**
3. Set `limit`: 50
4. Click **"Execute"**

**You'll see 377 item codes across 8 blocks:**
- Block 1: Identification (25 items)
- Block 3: Household characteristics (23 items)
- Block 4: Demographic particulars (81 items)
- Block 4.1: Migration status (32 items)
- Block 5.1: Usual principal status (70 items)
- Block 5.2: Usual subsidiary status (62 items)
- Block 5.3: Current weekly status (41 items)
- Block 6: Current daily status (43 items)

### Filter by Block:
1. Set `block`: Block 5.1
2. Set `limit`: 20
3. Click **"Execute"**

### Search Item Codes:
1. Set `search`: education
2. Click **"Execute"**

Finds all items related to education!

---

## 📑 Test 6: Get Dataset Records
**Endpoint:** `GET /api/v1/plfs/dataset/{id}/records`

### Get District Codes Records:
1. Click on **`GET /api/v1/plfs/dataset/{id}/records`**
2. Click **"Try it out"**
3. Set `id`: 2 (for District Codes)
4. Set `limit`: 50
5. Click **"Execute"**

**Returns 695 district codes with pagination!**

### Get Item Codes Records:
1. Set `id`: 3 (for Item Codes)
2. Set `limit`: 100
3. Click **"Execute"**

---

## 🔍 Real-World Query Examples

### Example 1: Find all education-related items
```
GET /api/v1/plfs/item-codes?search=education
```

### Example 2: Get Karnataka districts
```
GET /api/v1/plfs/district-codes?state=Karnataka
```

### Example 3: Get Block 4 demographic items
```
GET /api/v1/plfs/item-codes?block=Block 4&limit=100
```

### Example 4: Paginate through districts
```
GET /api/v1/plfs/district-codes?offset=0&limit=50    # First 50
GET /api/v1/plfs/district-codes?offset=50&limit=50   # Next 50
GET /api/v1/plfs/district-codes?offset=100&limit=50  # Next 50
```

---

## 🐍 Test via Python Script

If you prefer Python:

```python
import requests

# 1. Login
response = requests.post(
    "http://127.0.0.1:8080/api/v1/auth/login",
    data={"username": "testuser", "password": "password123"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Get PLFS Summary
response = requests.get(
    "http://127.0.0.1:8080/api/v1/plfs/summary",
    headers=headers
)
print(response.json())

# 3. Get District Codes
response = requests.get(
    "http://127.0.0.1:8080/api/v1/plfs/district-codes?limit=10",
    headers=headers
)
print(response.json())

# 4. Search Item Codes
response = requests.get(
    "http://127.0.0.1:8080/api/v1/plfs/item-codes?search=education",
    headers=headers
)
print(response.json())
```

---

## 🧪 Test via cURL

### Register:
```bash
curl -X POST "http://127.0.0.1:8080/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123","full_name":"Test User","role":"researcher"}'
```

### Login:
```bash
curl -X POST "http://127.0.0.1:8080/api/v1/auth/login" \
  -d "username=testuser&password=password123"
```

### Get PLFS Summary:
```bash
curl -X GET "http://127.0.0.1:8080/api/v1/plfs/summary" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get District Codes:
```bash
curl -X GET "http://127.0.0.1:8080/api/v1/plfs/district-codes?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📊 Data Statistics

### Real PLFS Data from microdata.gov.in:

| Dataset | Records | Description |
|---------|---------|-------------|
| **District Codes** | 695 | All districts from PLFS Panel 4 (2023-24) |
| **Data Layout** | 400 | PLFS structure with 4 sheets (Data Layout, State codes, chhv1, cperv1) |
| **Item Codes** | 377 | Survey items across 8 blocks |
| **TOTAL** | **1,472** | Real government survey data |

---

## ✅ What You Can Do With This Data

1. **Query District Codes**: 695 districts across all Indian states
2. **Explore Item Codes**: 377 survey items covering:
   - Demographics
   - Education levels
   - Employment status
   - Migration patterns
   - Household characteristics

3. **Understand Survey Structure**: Complete data layout and variable definitions

4. **Filter & Search**: 
   - By state
   - By block
   - By keyword
   - With pagination

5. **Analyze Real Data**: Actual PLFS survey structure from microdata.gov.in

---

## 🚀 Next Steps

1. **Ingest More Data**: 
   - Download more datasets from microdata.gov.in
   - Copy to `data/mospi_real_data/`
   - Run: `python ingest_mospi_data.py`

2. **Create Custom Queries**:
   - Combine multiple filters
   - Build data analysis pipelines
   - Export results for visualization

3. **Integrate into Applications**:
   - Use these APIs in your data portal
   - Build dashboards
   - Create reports

---

## 🎉 Success!

You now have **1,472 real PLFS records** from microdata.gov.in accessible via REST API!

**All 6 PLFS endpoints are working:**
✅ Summary endpoint  
✅ List datasets endpoint  
✅ District codes endpoint (695 districts)  
✅ Data layout endpoint (400 records)  
✅ Item codes endpoint (377 items)  
✅ Dataset records endpoint  

**Perfect for Statathon presentation! 🏆**
