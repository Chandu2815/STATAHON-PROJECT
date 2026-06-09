# Quick Start Guide

## Prerequisites
- Python 3.10+
- PostgreSQL 13+

## Installation Steps

### 1. Navigate to Project Directory
```powershell
cd "c:\Users\Dell\OneDrive\Desktop\Chandu\STATATHON\Statathon 2"
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```powershell
Copy-Item .env.example .env
# Edit .env with your database credentials
```

### 5. Initialize Database
Make sure PostgreSQL is running, then:
```powershell
python -m app.database
```

### 6. Load Sample Data
```powershell
# First, create the census data table in your database
python -c "from app.database import init_db; init_db()"

# Then ingest sample data
python -m app.services.ingestion --config config/datasets/census_dataset.yaml --data data/sample_census_data.csv
```

### 7. Run the Application
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Access the Application
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Testing the API

### 1. Register a User
```powershell
curl -X POST "http://localhost:8000/api/v1/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "securepassword123",
    "full_name": "Test User"
  }'
```

### 2. Login
```powershell
curl -X POST "http://localhost:8000/api/v1/auth/login" `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=testuser&password=securepassword123"
```

### 3. Query Data (with token)
```powershell
curl -X GET "http://localhost:8000/api/v1/query?dataset=census&state=Maharashtra&gender=Female&age_group=15-29" `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Docker Deployment

### Using Docker Compose
```powershell
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- API server

Access at: http://localhost:8000

## Project Features Demo

### Multi-dimensional Filtering
```
GET /api/v1/query?dataset=census&state=Maharashtra&gender=Female&age_group=15-29
```

### Usage Statistics
```
GET /api/v1/users/me/usage
```

### Credit Topup
```
POST /api/v1/users/me/topup?amount=50
```

### Premium Upgrade
```
POST /api/v1/users/me/upgrade-premium
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Verify credentials

### Import Errors
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

### Port Already in Use
- Change port: `uvicorn app.main:app --port 8001`

## Next Steps
1. Explore API documentation at /docs
2. Try different query filters
3. Check usage metering
4. Test rate limiting
5. Explore admin features (if admin user)
