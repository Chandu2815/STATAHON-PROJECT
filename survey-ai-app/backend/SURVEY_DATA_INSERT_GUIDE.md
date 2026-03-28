"""
Integration Guide: Survey Data Insert Router
How to integrate the survey_data_insert router into your FastAPI backend
"""

# ============================================================================
# Step 1: Add to main.py
# ============================================================================

"""
In your survey-ai-app/backend/main.py, add the import and include_router:

from fastapi import FastAPI
from routers.survey_data_insert import router as survey_data_router

app = FastAPI(
    title="Survey AI Backend",
    description="Dataset and Analytics Service"
)

# Include the survey data insert router
app.include_router(survey_data_router)

# Endpoints will be available at:
# POST   /survey-data/insert
# POST   /survey-data/insert-safe
# GET    /survey-data/stats
"""

# ============================================================================
# Step 2: API Usage Examples
# ============================================================================

"""
# Example 1: Insert single record
POST /survey-data/insert
Content-Type: application/json

{
    "skip_duplicates": true,
    "records": [
        {
            "dataset_name": "HCES 2022",
            "category": "HCES",
            "year": 2022,
            "indicator_name": "Total Consumption Expenditure",
            "value": 5280.50,
            "state": "Bihar",
            "district": "Patna"
        }
    ]
}

Response (201 Created):
{
    "success": true,
    "inserted_count": 1,
    "skipped_count": 0,
    "total_processed": 1,
    "duplicates": [],
    "errors": []
}


# Example 2: Bulk insert with duplicates
POST /survey-data/insert
Content-Type: application/json

{
    "skip_duplicates": true,
    "records": [
        {
            "dataset_name": "HCES 2022",
            "category": "HCES",
            "year": 2022,
            "indicator_name": "Total Consumption",
            "value": 5280.50,
            "state": "Bihar",
            "district": "Patna"
        },
        {
            "dataset_name": "HCES 2022",
            "category": "HCES",
            "year": 2022,
            "indicator_name": "Food Expenditure",
            "value": 1200.25,
            "state": "Bihar",
            "district": "Patna"
        },
        {
            "dataset_name": "HCES 2022",
            "category": "HCES",
            "year": 2022,
            "indicator_name": "Total Consumption",  // DUPLICATE
            "value": 5280.50,
            "state": "Bihar",
            "district": "Patna"
        }
    ]
}

Response (201 Created):
{
    "success": true,
    "inserted_count": 2,
    "skipped_count": 1,
    "total_processed": 3,
    "duplicates": [
        {
            "record_index": 2,
            "dataset_name": "HCES 2022",
            "state": "Bihar",
            "year": 2022,
            "indicator_name": "Total Consumption"
        }
    ],
    "errors": []
}


# Example 3: Get table statistics
GET /survey-data/stats

Response (200 OK):
{
    "success": true,
    "data": {
        "total_records": 15420,
        "dataset_count": 3,
        "datasets": ["HCES 2022", "PLFS 2023", "Survey 2022"],
        "category_count": 2,
        "categories": ["HCES", "PLFS"],
        "year_range": {
            "min": 2020,
            "max": 2023
        },
        "state_count": 28,
        "states": ["Andaman and Nicobar", "Andhra Pradesh", ..., "West Bengal"]
    },
    "meta": {
        "timestamp": "2026-03-28T10:30:00"
    }
}
"""

# ============================================================================
# Step 3: Database Requirements
# ============================================================================

"""
Ensure your survey_data table exists with the following schema:

CREATE TABLE IF NOT EXISTS survey_data (
    id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL CHECK (year >= 1900 AND year <= 2100),
    indicator_name VARCHAR(255) NOT NULL,
    value FLOAT NOT NULL,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint to prevent duplicates
    UNIQUE(dataset_name, year, indicator_name, state, COALESCE(district, ''))
);

-- Create indexes for faster queries
CREATE INDEX idx_survey_data_dataset ON survey_data(dataset_name);
CREATE INDEX idx_survey_data_year ON survey_data(year);
CREATE INDEX idx_survey_data_category ON survey_data(category);
CREATE INDEX idx_survey_data_state ON survey_data(state);
CREATE INDEX idx_survey_data_district ON survey_data(district);
CREATE INDEX idx_survey_data_indicator ON survey_data(indicator_name);
"""

# ============================================================================
# Step 4: Python/Frontend Integration
# ============================================================================

"""
# Python (requests library)
import requests
import json

# Insert records
url = "http://localhost:8001/survey-data/insert"
payload = {
    "skip_duplicates": True,
    "records": [
        {
            "dataset_name": "HCES 2022",
            "category": "HCES",
            "year": 2022,
            "indicator_name": "Total Consumption",
            "value": 5280.50,
            "state": "Bihar",
            "district": "Patna"
        }
    ]
}

response = requests.post(url, json=payload)
print(response.json())


# JavaScript/React
const insertRecords = async (records) => {
    const response = await fetch('http://localhost:8001/survey-data/insert', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            skip_duplicates: true,
            records: records
        })
    });
    
    return await response.json();
};

// Usage
insertRecords([
    {
        dataset_name: "HCES 2022",
        category: "HCES",
        year: 2022,
        indicator_name: "Total Consumption",
        value: 5280.50,
        state: "Bihar",
        district: "Patna"
    }
]).then(result => console.log(result));


# cURL
curl -X POST http://localhost:8001/survey-data/insert \\
  -H "Content-Type: application/json" \\
  -d '{
    "skip_duplicates": true,
    "records": [
      {
        "dataset_name": "HCES 2022",
        "category": "HCES",
        "year": 2022,
        "indicator_name": "Total Consumption",
        "value": 5280.50,
        "state": "Bihar",
        "district": "Patna"
      }
    ]
  }'
"""

# ============================================================================
# Step 5: Error Handling
# ============================================================================

"""
The endpoint returns proper HTTP status codes:

200 OK (GET /survey-data/stats)
    - Statistics retrieved successfully

201 Created (POST /survey-data/insert, POST /survey-data/insert-safe)
    - Records inserted successfully

400 Bad Request
    - Missing required fields
    - Empty records array
    - Records exceed 10,000 limit
    
    Example error response:
    {
        "detail": "At least one record is required"
    }

422 Unprocessable Entity
    - Validation error (e.g., year out of range)
    - Invalid data type
    
    Example error response:
    {
        "detail": [
            {
                "loc": ["body", "records", 0, "year"],
                "msg": "ensure this value is less than or equal to 2100",
                "type": "value_error.number.not_le",
                "ctx": {"limit_value": 2100}
            }
        ]
    }

500 Internal Server Error
    - Database connection failed
    - Transaction error
    
    Example error response:
    {
        "detail": "Database transaction failed: connection pool timeout"
    }
"""

# ============================================================================
# Step 6: Endpoints Summary
# ============================================================================

"""
POST /survey-data/insert
    Purpose: Bulk insert survey records with transaction management
    Max Records: 10,000 per request
    Duplicate Handling: Skip or fail (configurable)
    Error Handling: Fails entire transaction on error
    Use Case: Batch imports where all-or-nothing is needed

POST /survey-data/insert-safe
    Purpose: Bulk insert with lenient error handling
    Max Records: 10,000 per request
    Duplicate Handling: Always skip
    Error Handling: Continues on individual record errors
    Use Case: Data imports with potential inconsistencies

GET /survey-data/stats
    Purpose: Get table statistics and metadata
    Returns: Record count, datasets, categories, year range, states
    Use Case: UI display, data validation, monitoring
"""

# ============================================================================
# Step 7: Integration with Survey-AI Dataset Explorer
# ============================================================================

"""
This endpoint is compatible with the Survey-AI dataset explorer:

1. After inserting data, update dataset hierarchy:
   - Call GET /datasets/hierarchical to refresh the dataset list
   
2. Dataset metadata becomes available:
   - GET /datasets/{dataset_id}/metadata shows new columns

3. Analytics queries work with new data:
   - POST /analytics/query can filter/aggregate new records

4. Frontend features enabled:
   - Dataset selector dropdown includes new dataset_name values
   - Column explorer shows: dataset_name, category, year, indicator_name, etc.
   - Filtering by state/district/year works immediately
   - Analytics charts can visualize the new data
"""

# ============================================================================
# Step 8: Performance Notes
# ============================================================================

"""
Optimization recommendations:

1. Batch Size
   - Use 1,000-5,000 records per request for optimal performance
   - File uploads: Import larger files in multiple batches

2. Duplicate Checking
   - The endpoint uses UNIQUE constraint for efficiency
   - Parametrized queries prevent SQL injection
   - Individual duplicate checks for clarity

3. Connection Management
   - Database connection pooling handles concurrency
   - Each request uses SQLAlchemy dependency injection

4. Indexes
   - Create indexes on frequently queried columns:
     - dataset_name, year, category, state, district, indicator_name

5. Transaction Management
   - POST /insert: Full transaction (all-or-nothing)
   - POST /insert-safe: Per-record commit (more resilient)
"""

# ============================================================================
# Step 9: Testing Examples
# ============================================================================

"""
# pytest integration test

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_insert_single_record():
    response = client.post(
        "/survey-data/insert",
        json={
            "skip_duplicates": True,
            "records": [
                {
                    "dataset_name": "HCES 2022",
                    "category": "HCES",
                    "year": 2022,
                    "indicator_name": "Test Indicator",
                    "value": 100.0,
                    "state": "Bihar",
                    "district": "Patna"
                }
            ]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["inserted_count"] >= 0
    assert data["total_processed"] == 1

def test_insert_invalid_year():
    response = client.post(
        "/survey-data/insert",
        json={
            "skip_duplicates": True,
            "records": [
                {
                    "dataset_name": "HCES 2022",
                    "category": "HCES",
                    "year": 3000,  # Invalid
                    "indicator_name": "Test",
                    "value": 100.0,
                    "state": "Bihar"
                }
            ]
        }
    )
    
    assert response.status_code == 422

def test_get_stats():
    response = client.get("/survey-data/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "total_records" in data["data"]
"""
