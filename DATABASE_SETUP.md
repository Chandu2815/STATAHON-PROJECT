# PostgreSQL FastAPI Setup Guide

## Overview
This guide explains the production-ready setup for connecting FastAPI to PostgreSQL using SQLAlchemy.

## Files Structure

```
project/
├── main.py                 # FastAPI application with endpoints
├── db.py                  # Database configuration & session management
├── db_connection.py       # Legacy (deprecated)
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── test_db_connection.py  # Connection testing script
└── DATABASE_SETUP.md      # This file
```

---

## Installation & Setup

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv
```

### 2. Configure Database Connection

Create a `.env` file in your project root:

```env
DATABASE_URL=postgresql://postgres:NewPassword123@187.127.138.4:5432/statahon_db
DEBUG=True
```

### 3. Create Database Tables

Connect to PostgreSQL and create the `survey_data` table:

```bash
psql -U postgres -h 127.0.0.1 -d survey_db
```

Then execute:

```sql
CREATE TABLE IF NOT EXISTS survey_data (
    id BIGSERIAL PRIMARY KEY,
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for better query performance
CREATE INDEX idx_survey_data_created_at ON survey_data(created_at DESC);
```

### 4. Test Database Connection

Run the validation script:

```bash
python test_db_connection.py
```

Expected output:
```
✓ DATABASE_URL loaded successfully
✓ SQLAlchemy 2.0.36
✓ psycopg2 2.9.10
✓ FastAPI 0.115.6
✓ Database connection successful
✓ Found 1 table(s):
  - survey_data (3 columns)
✓ survey_data table exists
✓ ALL TESTS PASSED
```

---

## Key Components Explained

### db.py - Database Configuration

**DATABASE_URL:**
- Format: `postgresql://user:password@host:port/database`
- Example: `postgresql://postgres:NewPassword123@187.127.138.4:5432/statahon_db`

**Connection Pool:**
- `pool_size=10` - Maintains 10 connections
- `max_overflow=20` - Can create up to 20 additional connections
- `pool_pre_ping=True` - Tests connections before using them
- Prevents "connection closed" errors

**Session Management:**
- `get_db()` dependency yields a session
- Session automatically closes after request
- Used with `Depends(get_db)` in FastAPI routes

### main.py - FastAPI Application

**Dependency Injection:**
```python
@app.post("/add")
async def add_survey_data(
    request: SurveyDataRequest,
    db: Session = Depends(get_db)  # <-- Dependency
):
    # db session is automatically managed
```

**Parameterized Queries:**
```python
query = text("INSERT INTO survey_data (data) VALUES (:data)")
db.execute(query, {"data": data_json})
```
Prevents SQL injection attacks.

---

## API Endpoints

### 1. Root Endpoint
```
GET /
```
Response:
```json
{
  "message": "Survey Data API is running",
  "status": "online",
  "version": "2.0.0",
  "docs": "/docs"
}
```

### 2. Health Check
```
GET /health
```
Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "api": "running"
}
```

### 3. Add Survey Data
```
POST /add
Content-Type: application/json

{
  "data": {
    "name": "John Doe",
    "age": 30,
    "region": "North"
  }
}
```

Response:
```json
{
  "message": "Survey data inserted successfully",
  "status": "created",
  "id": 1,
  "created_at": "2024-03-24T10:30:00.123456",
  "data": {
    "name": "John Doe",
    "age": 30,
    "region": "North"
  }
}
```

### 4. Get All Data
```
GET /data
```

### 5. Get Specific Record
```
GET /data/{record_id}
```

### 6. Database Status
```
GET /status/db
```

---

## Common Issues & Solutions

### Issue 1: "Connection refused"
**Symptoms:** `Error: could not connect to server: Connection refused`

**Solution:**
```bash
# Check if PostgreSQL is running
systemctl status postgresql

# Start PostgreSQL if stopped
systemctl start postgresql

# Verify connection manually
psql -U postgres -h 127.0.0.1 -d survey_db
```

### Issue 2: "FATAL: Ident authentication failed"
**Symptoms:** `Error: FATAL: Ident authentication failed for user "postgres"`

**Solution:** 
The database URL format is incorrect. Ensure:
- Password is URL encoded if it contains special characters
- Example: `@:P@ssw0rd!` → `@%3AP%40ssw0rd%21`
 - Use this format: `postgresql://postgres:NewPassword123@187.127.138.4:5432/statahon_db`

### Issue 3: "Database survey_db does not exist"
**Symptoms:** `Error: database "survey_db" does not exist`

**Solution:**
```bash
# Create the database
psql -U postgres -h 127.0.0.1

# In psql:
CREATE DATABASE survey_db;

# Then create the table
\c survey_db

CREATE TABLE survey_data (
    id BIGSERIAL PRIMARY KEY,
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Issue 4: "500 Internal Server Error - Database error"
**Symptoms:** Requests fail with database errors

**Solution:**
1. Run test script: `python test_db_connection.py`
2. Check `.env` file for correct DATABASE_URL
3. Verify PostgreSQL user permissions:
```sql
GRANT ALL PRIVILEGES ON DATABASE survey_db TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
```

### Issue 5: "Connection pool exhausted"
**Symptoms:** `QueuePool timeout error`

**Solution:** Increase pool size in `db.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,      # Increase from 10
    max_overflow=40    # Increase from 20
)
```

---

## Running the Application

### Development Mode
```bash
python main.py
```

Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
✓ Database connection verified at startup
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Testing with cURL

### Test health endpoint
```bash
curl -X GET http://localhost:8000/health
```

### Add survey data
```bash
curl -X POST http://localhost:8000/add \
  -H "Content-Type: application/json" \
  -d '{"data": {"name": "Alice", "region": "South"}}'
```

### Get all data
```bash
curl -X GET http://localhost:8000/data
```

### Get specific record
```bash
curl -X GET http://localhost:8000/data/1
```

---

## Why SQLAlchemy Over Raw psycopg2?

| Feature | psycopg2 | SQLAlchemy |
|---------|----------|-----------|
| Connection Pooling | Manual | Built-in |
| Session Management | Manual | Automatic |
| Error Handling | Manual | Automatic |
| Type Safety | No | Yes (with ORM) |
| Dependency Injection | No | Compatible |
| Code Reuse | Limited | High |
| Production Readiness | Requires setup | Out of box |

---

## Environment Variables Best Practices

✅ **DO:**
- Store `DATABASE_URL` in `.env`
- Use `python-dotenv` to load it
- Never commit `.env` to version control
- Add `.env` to `.gitignore`
- Use different URLs for dev/prod

❌ **DON'T:**
- Hardcode credentials in code
- Commit `.env` to Git
- Use same credentials for dev and prod
- Store passwords in comments
- Share the `.env` file unencrypted

---

## Performance Tips

1. **Enable Connection Pooling:** Already configured in `db.py`
2. **Use Indexes:** Created in table setup
3. **Cache Connections:** SQLAlchemy pool handles this
4. **Batch Operations:** For bulk inserts, use transactions
5. **Query Optimization:** Use specific columns in SELECT

---

## Next Steps

1. ✓ Database connection is verified
2. ✓ FastAPI app is running
3. Add authentication (optional)
4. Add request validation (already done with Pydantic)
5. Add logging and monitoring
6. Deploy to production server

---

For more help:
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- FastAPI Docs: https://fastapi.tiangolo.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/
