"""
QUICK START: Survey Data Insert Endpoint
Get the endpoint running in 5 minutes
"""

# ============================================================================
# 1. Update main.py to include the router
# ============================================================================

"""
File: survey-ai-app/backend/main.py

Add these lines:
"""

# At the top with other imports:
from routers.survey_data_insert import router as survey_data_router

# In the app initialization section, add:
def create_app():
    app = FastAPI(
        title="Survey AI Backend",
        description="Dataset and Analytics Service",
        version="1.0.0"
    )
    
    # Include routers
    app.include_router(survey_data_router)
    
    return app

app = create_app()


# ============================================================================
# 2. Ensure database table exists
# ============================================================================

"""
Run this SQL in your PostgreSQL database:

psql -U postgres -d survey_db -c "
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
    
    UNIQUE(dataset_name, year, indicator_name, state, COALESCE(district, ''))
);

CREATE INDEX IF NOT EXISTS idx_survey_data_dataset ON survey_data(dataset_name);
CREATE INDEX IF NOT EXISTS idx_survey_data_year ON survey_data(year);
CREATE INDEX IF NOT EXISTS idx_survey_data_category ON survey_data(category);
CREATE INDEX IF NOT EXISTS idx_survey_data_state ON survey_data(state);
CREATE INDEX IF NOT EXISTS idx_survey_data_district ON survey_data(district);
CREATE INDEX IF NOT EXISTS idx_survey_data_indicator ON survey_data(indicator_name);
"
"""

# ============================================================================
# 3. Start the FastAPI backend
# ============================================================================

"""
cd /Users/arunsudhaveni/STATAHON\ PROJECT/survey-ai-app/backend
source ../../.venv/bin/activate
python main.py

Expected output:
    ✅ Database connection: OK
    ✅ Application started
    ✅ API running on http://localhost:8001
    ✅ Endpoints available:
        POST   /survey-data/insert
        POST   /survey-data/insert-safe
        GET    /survey-data/stats
"""

# ============================================================================
# 4. Test the endpoint
# ============================================================================

"""
Option A: Using cURL

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

Expected response:
{
    "success": true,
    "inserted_count": 1,
    "skipped_count": 0,
    "total_processed": 1,
    "duplicates": [],
    "errors": []
}


Option B: Using Python

import requests

response = requests.post(
    'http://localhost:8001/survey-data/insert',
    json={
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
)

print(response.json())


Option C: Using Interactive API Docs

1. Start the backend
2. Open http://localhost:8001/docs
3. Find the "POST /survey-data/insert" endpoint
4. Click "Try it out"
5. Enter JSON payload
6. Click "Execute"
"""

# ============================================================================
# 5. Load data from CSV
# ============================================================================

"""
Option A: Using the CSV Loader Script

cd /Users/arunsudhaveni/STATAHON\ PROJECT/survey-ai-app/backend

# Load DataSet.csv
python csv_loader.py "../../data/Data in CSV (1)/DataSet.csv"

# Expected output:
    Loading CSV from: ../../data/Data in CSV (1)/DataSet.csv
    Loaded 15420 rows from CSV
    Columns: ['dataset_name', 'category', 'year', 'indicator_name', 'value', 'state', 'district']
    Transformed 15312 valid records from 15420 CSV rows
    Processing 15312 records in 16 batches...
    
    Batch 1/16
    Inserting batch of 1000 records...
    Batch result: 998 inserted, 2 skipped, 0 errors
    
    ... (more batches)
    
    === Load & Insert Complete ===
    Total Inserted: 15100
    Total Skipped: 212
    Total Errors: 0
    Batches Processed: 16


Option B: Manual batch loading

# Create a simple Python script:

from csv_loader import SurveyDataCSVLoader

loader = SurveyDataCSVLoader(batch_size=2000)
stats = loader.load_and_insert(
    filepath="../../data/Data in CSV (1)/DataSet.csv",
    skip_duplicates=True
)

print(f"Inserted: {stats['total_inserted']}")
print(f"Skipped: {stats['total_skipped']}")
print(f"Errors: {stats['total_errors']}")
"""

# ============================================================================
# 6. Query the inserted data
# ============================================================================

"""
Option A: Get statistics

curl http://localhost:8001/survey-data/stats

Response:
{
    "success": true,
    "data": {
        "total_records": 15100,
        "dataset_count": 3,
        "datasets": ["HCES 2022", "PLFS 2023", "Survey 2022"],
        "category_count": 2,
        "categories": ["HCES", "PLFS"],
        "year_range": {
            "min": 2020,
            "max": 2023
        },
        "state_count": 28,
        "states": ["Andhra Pradesh", "Bihar", "Delhi", ...]
    },
    "meta": {
        "timestamp": "2026-03-28T10:30:00"
    }
}


Option B: Verify data in database

psql -U postgres -d survey_db -c "SELECT COUNT(*) FROM survey_data;"
psql -U postgres -d survey_db -c "SELECT DISTINCT dataset_name FROM survey_data;"
psql -U postgres -d survey_db -c "SELECT * FROM survey_data LIMIT 5;"
"""

# ============================================================================
# 7. Integrate with Survey-AI frontend
# ============================================================================

"""
The inserted data is now available in the Survey-AI frontend:

1. Dataset Dropdown:
   - GET /datasets/hierarchical will include the new data
   - Users can select dataset_name from the dropdown

2. Data Explorer:
   - Dataset selector shows all inserted dataset_name values
   - Users can filter by year, state, district
   - Columns are automatically detected

3. Analytics:
   - Charts can be generated from the value column
   - Grouping by state/district/year is supported
   - Aggregations work with the data

Frontend code (React):

import React, { useEffect, useState } from 'react';

function SurveyDataLoader() {
  const [status, setStatus] = useState('');

  const loadData = async () => {
    setStatus('Loading...');
    try {
      const response = await fetch('http://localhost:8001/survey-data/stats');
      const stats = await response.json();
      setStatus(`Loaded ${stats.data.total_records} records`);
    } catch (err) {
      setStatus('Error: ' + err.message);
    }
  };

  return (
    <div>
      <button onClick={loadData}>Load Survey Data</button>
      <p>{status}</p>
    </div>
  );
}

export default SurveyDataLoader;
"""

# ============================================================================
# 8. Troubleshooting
# ============================================================================

"""
Problem: "Connection refused" error
Solution:
  - Make sure PostgreSQL is running: pg_isready
  - Check DATABASE_URL in main.py
  - Verify database exists: psql -l

Problem: "Table survey_data does not exist"
Solution:
  - Run the SQL CREATE TABLE command from step 2
  - Check table: psql -U postgres -d survey_db -c "\\dt"

Problem: "Validation error" on year field
Solution:
  - Year must be between 1900 and 2100
  - Ensure CSV has valid year values
  - Check data types in CSV file

Problem: "Duplicate key value violates unique constraint"
Solution:
  - Use skip_duplicates: true (default)
  - Or delete existing records: TRUNCATE TABLE survey_data;

Problem: "Request timeout"
Solution:
  - Reduce batch size: python csv_loader.py file.csv --batch-size 500
  - Check database performance
  - Ensure sufficient RAM/disk space

Problem: CSV has different column names
Solution:
  - Common mappings in csv_loader.py:
    'indicator' → 'indicator_name'
    'amount' → 'value'
    'quantity' → 'value'
  - Or provide custom mapping
"""

# ============================================================================
# 9. Performance Tips
# ============================================================================

"""
For optimal performance:

1. Batch Size
   - 1,000-5,000 records per request is ideal
   - 10,000 is the maximum
   - Smaller batches = slower but more reliable

2. Indexes
   - Ensure all indexes are created
   - Query performance improves significantly
   - Check: psql -U postgres -d survey_db -c "\\di"

3. Connection Pooling
   - FastAPI uses SQLAlchemy connection pooling
   - Pool size: 10, max_overflow: 20 (default)
   - Tune if you have many concurrent users

4. Database Maintenance
   - Regular VACUUM: psql -U postgres -d survey_db -c "VACUUM ANALYZE;"
   - Check query performance: EXPLAIN ANALYZE <query>

5. Monitoring
   - Monitor: SELECT COUNT(*) FROM survey_data;
   - Check growth: SELECT DATE(created_at), COUNT(*) FROM survey_data GROUP BY 1;
"""

# ============================================================================
# 10. Next Steps
# ============================================================================

"""
After data is loaded:

1. Test API endpoints
   - Use OpenAPI docs: http://localhost:8001/docs
   - Try different queries
   - Test error cases

2. Verify data quality
   - Check for NULL values
   - Verify year range
   - Compare with original CSV

3. Set up monitoring
   - Log insert operations
   - Track error rates
   - Monitor database size

4. Integrate with UI
   - Update Dataset Explorer
   - Configure data visualization
   - Add filtering options

5. Set up automated imports
   - Schedule CSV uploads
   - Create data pipeline
   - Add data validation

6. Performance optimization
   - Profile queries
   - Optimize indexes
   - Plan capacity
"""
