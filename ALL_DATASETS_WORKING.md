# All Datasets Working - Quick Guide

## ✅ All 5 Datasets Now Accessible

Your MoSPI Data Portal now has **5 datasets** working with **517,029 total records**:

| Dataset ID | Name | Storage Type | Records | Status |
|------------|------|--------------|---------|---------|
| 1 | PLFS Data Layout | data_records (JSON) | 400 | ✅ |
| 2 | PLFS District Codes | data_records (JSON) | 695 | ✅ |
| 3 | PLFS Item Codes | data_records (JSON) | 377 | ✅ |
| 4 | Household Survey (CHHV1) | Dedicated Table | 101,957 | ✅ |
| 5 | Person Survey (CPERV1) | Dedicated Table | 413,549 | ✅ |

## 📊 How to Query Each Dataset

### Option 1: Query by Dataset ID (Works for ALL datasets)

```bash
# Dataset 1: Data Layout
GET /api/v1/query/dataset/1/records?limit=10

# Dataset 2: District Codes
GET /api/v1/query/dataset/2/records?limit=10
GET /api/v1/query/dataset/2/records?filters={"State": "PUNJAB"}

# Dataset 3: Item Codes
GET /api/v1/query/dataset/3/records?limit=10

# Dataset 4: Household Survey
GET /api/v1/query/dataset/4/records?limit=10
GET /api/v1/query/dataset/4/records?filters={"State_Ut_Code": 28}

# Dataset 5: Person Survey
GET /api/v1/query/dataset/5/records?limit=10
GET /api/v1/query/dataset/5/records?filters={"Age": {"$gte": 25, "$lte": 35}}
```

### Option 2: Query by Table Name (For dedicated tables only)

```bash
# Household Survey (Dataset 4)
GET /api/v1/query/household_survey?limit=10
GET /api/v1/query/household_survey?filters={"State_Ut_Code": 28}&fields=State_Ut_Code,District_Code,Monthly_Consumer_Expenditure

# Person Survey (Dataset 5)
GET /api/v1/query/person_survey?limit=10
GET /api/v1/query/person_survey?filters={"Age": {"$gte": 25, "$lte": 35}, "Sex": 1}
```

## 🔍 Get Schema Information

```bash
# Get schema for any dataset
GET /api/v1/datasets/1/schema  # Data Layout (JSON storage)
GET /api/v1/datasets/2/schema  # District Codes (JSON storage)
GET /api/v1/datasets/3/schema  # Item Codes (JSON storage)
GET /api/v1/datasets/4/schema  # Household Survey (dedicated table)
GET /api/v1/datasets/5/schema  # Person Survey (dedicated table)
```

The schema endpoint now handles both storage types:
- **JSON storage**: Shows fields from sample records in data_records table
- **Dedicated tables**: Shows actual database columns with types and indexes

## 📋 List All Available Datasets

```bash
# Public endpoint - no authentication required
GET /api/v1/datasets/tables

# Shows all tables with:
# - Row counts
# - Column counts  
# - Sample columns
# - Query endpoints
```

## 🔐 Authentication

All query endpoints require authentication:

1. **Register a user:**
```bash
POST /api/v1/auth/register
{
  "username": "yourname",
  "email": "you@example.com",
  "password": "yourpassword",
  "role": "PUBLIC"
}
```

2. **Login to get token:**
```bash
POST /api/v1/auth/login
Form data: username=yourname&password=yourpassword
```

3. **Use token in requests:**
```bash
GET /api/v1/query/person_survey?limit=10
Header: Authorization: Bearer YOUR_TOKEN_HERE
```

## 💡 Example Queries

### Get Maharashtra households with high expenditure
```bash
GET /api/v1/query/household_survey?filters={"State_Ut_Code": 28, "Monthly_Consumer_Expenditure": {"$gte": 10000}}
```

### Get employed persons aged 25-35
```bash
GET /api/v1/query/person_survey?filters={"Age": {"$gte": 25, "$lte": 35}, "Current_Weekly_Activity_Status": 11}
```

### Get district codes for a specific state
```bash
GET /api/v1/query/dataset/2/records?filters={"State": "PUNJAB"}
```

### Get item codes for a specific block
```bash
GET /api/v1/query/dataset/3/records?filters={"Block No.": "3"}
```

## 📖 API Documentation

Open in your browser: **http://localhost:8080/docs**

All endpoints are documented with:
- Parameter descriptions
- Example requests
- Response schemas
- Try-it-out functionality

## ✅ What Was Fixed

1. **Schema endpoint** - Now handles both storage types (data_records JSON and dedicated tables)
2. **Query by ID endpoint** - New `/query/dataset/{id}/records` works for all datasets
3. **Storage detection** - Automatically detects if dataset uses dedicated table or data_records
4. **Filter support** - JSON filters work for both storage types
5. **Row counts** - Accurate counts for all datasets

All 5 datasets are now fully functional and queryable!
