# FastAPI + PostgreSQL Production-Ready Setup

## Overview

This is a **production-ready FastAPI backend** integrated with PostgreSQL 16 using SQLAlchemy for robust database connection management.

### What's Included

✅ SQLAlchemy ORM with connection pooling  
✅ FastAPI with dependency injection  
✅ Parameterized queries (SQL injection prevention)  
✅ Environment-based configuration (.env)  
✅ Comprehensive error handling  
✅ Health check endpoints  
✅ Connection validation  
✅ API documentation (Swagger/ReDoc)  

---

## Quick Start

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Create Database & Table

**Option A: Using SQL Script**

```bash
# On your VPS terminal
psql -U postgres -h 127.0.0.1

# In psql, run:
\i setup.sql
```

**Option B: Using psql Commands Directly**

```bash
# Create database
psql -U postgres -h 127.0.0.1 -c "CREATE DATABASE survey_db;"

# Create table
psql -U postgres -h 127.0.0.1 -d survey_db -c "
CREATE TABLE survey_data (
    id BIGSERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"
```

### 3️⃣ Verify Environment Configuration

**File: `.env`** (already created)
```env
DATABASE_URL=postgresql://postgres:NewPassword123@187.127.138.4:5432/statahon_db
DEBUG=True
```

### 4️⃣ Test Database Connection

```bash
python test_db_connection.py
```

Expected output:
```
✓ DATABASE_URL loaded successfully
✓ SQLAlchemy 2.0.36
✓ psycopg2 2.9.10
✓ Database connection successful
✓ Found 1 table(s): survey_data (3 columns)
✓ ALL TESTS PASSED
```

### 5️⃣ Start the API Server

```bash
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
✓ Database connection verified at startup
```

---

## API Endpoints

### 1. Root Endpoint
```bash
curl -X GET http://localhost:8000/
```

### 2. Health Check
```bash
curl -X GET http://localhost:8000/health
```

### 3. Add Survey Data
```bash
curl -X POST http://localhost:8000/add \
  -H "Content-Type: application/json" \
  -d '{"data": {"name": "Alice", "age": 30, "region": "North"}}'
```

### 4. Fetch All Data
```bash
curl -X GET http://localhost:8000/data
```

### 5. Fetch Specific Record
```bash
curl -X GET http://localhost:8000/data/1
```

### 6. Database Status
```bash
curl -X GET http://localhost:8000/status/db
```

---

## API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## File Structure

```
project/
├── main.py                    # FastAPI application (v2.0 with SQLAlchemy)
├── db.py                      # Database configuration & session management
├── db_connection.py           # Legacy (deprecated, kept for reference)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── setup.sql                  # SQL setup script for database & table
├── test_db_connection.py      # Connection testing & diagnostics
├── setup_verify.py            # Verification script
├── DATABASE_SETUP.md          # Detailed setup guide
└── PRODUCTION_SETUP.md        # This file
```

---

## Key Improvements Over v1.0

### Old Approach (db_connection.py + v1 main.py)
❌ Manual connection management  
❌ No connection pooling  
❌ Manual cursor closing  
❌ Manual transaction management  
❌ Potential memory leaks  
❌ No dependency injection  

### New Approach (db.py + v2 main.py)
✅ SQLAlchemy connection pooling  
✅ Automatic connection reuse  
✅ Automatic resource cleanup  
✅ FastAPI dependency injection  
✅ Built-in error handling  
✅ Production-ready  

---

## Common Mistakes & Fixes

### ❌ Error: "database survey_db does not exist"
```bash
# Fix: Create the database first
psql -U postgres -h 127.0.0.1 -c "CREATE DATABASE survey_db;"
```

### ❌ Error: "connection to server failed"
```bash
# Fix: Verify PostgreSQL is running
sudo systemctl status postgresql

# Start if stopped
sudo systemctl start postgresql
```

### ❌ Error: "FATAL: Ident authentication failed"
```bash
# Fix: Use correct URL format
# Wrong: postgresql://postgres:password@localhost/survey_db
# Right: postgresql://postgres:NewPassword123@187.127.138.4:5432/statahon_db
```

### ❌ Error: "pool timeout"
```python
# Fix: Increase pool size in db.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Increase
    max_overflow=40         # Increase
)
```

---

## Connection Pool Explained

```python
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,          # Idle connections maintained
    max_overflow=20,       # Additional connections when needed
    pool_pre_ping=True     # Validate connections before use
)
```

**Benefits:**
- Reuses connections (fast)
- Prevents "connection closed" errors
- Auto-recovers broken connections
- Thread-safe for concurrent requests

---

## Database Dependency Injection

```python
# In any route:
@app.get("/data")
async def get_data(db: Session = Depends(get_db)):
    # db session is automatically created
    result = db.execute(text("SELECT * FROM survey_data"))
    # db session is automatically closed after response
    return result.fetchall()
```

**Advantages:**
- No manual session management
- Automatic cleanup
- Thread-safe
 - Easy to test with testing harnesses

---

## Production Deployment

### Using Gunicorn + Uvicorn

```bash
# Install
pip install gunicorn python-dotenv

# Run with 4 workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
```

### Using Systemd Service

**File: `/etc/systemd/system/fastapi.service`**

```ini
[Unit]
Description=FastAPI Survey Data API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/user/project
ExecStart=/usr/bin/python3 main.py
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start fastapi
sudo systemctl enable fastapi
```

### Using Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t fastapi-survey .
docker run -p 8000:8000 --env-file .env fastapi-survey
```

---

## Monitoring & Debugging

### View Logs
```bash
tail -f /var/log/fastapi.log
```

### Debug Mode
```python
# In db.py, set:
engine = create_engine(DATABASE_URL, echo=True)  # Shows SQL queries
```

### Test Specific Endpoint
```bash
python -c "
from db import test_connection
result = test_connection()
print(result)
"
```

---

## Performance Tips

1. **Connection Pooling:** Already optimized in `db.py`
2. **Database Indexes:** Created in `setup.sql`
3. **Query Optimization:** Use specific columns in SELECT
4. **Caching:** Add Redis for frequently accessed data
5. **Async Operations:** FastAPI handles concurrency out of box

---

## Security Best Practices

✅ **Use environment variables** for credentials (done via .env)  
✅ **Never commit .env** to Git (add to .gitignore)  
✅ **Use parameterized queries** (SQLAlchemy does this automatically)  
✅ **Validate input** with Pydantic models (done)  
✅ **Use HTTPS** in production (configure nginx/Caddy)  
✅ **Add authentication** (implement JWT if needed)  
✅ **Limit request rate** (use slowapi middleware)  

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | postgresql://postgres:NewPassword123@187.127.138.4:5432/statahon_db | Database connection string |
| `DEBUG` | True | Enable debug mode (set False in production) |
| `DB_POOL_SIZE` | 10 | Connection pool size |
| `DB_MAX_OVERFLOW` | 20 | Max overflow connections |

---

## Troubleshooting Checklist

- [ ] PostgreSQL is running: `systemctl status postgresql`
- [ ] Database exists: `psql -l | grep survey_db`
- [ ] Table exists: `psql -d survey_db -c "\dt"`
- [ ] .env file is in project root
- [ ] DATABASE_URL is correct in .env
- [ ] All packages installed: `pip list | grep sqlalchemy`
- [ ] Test connection passes: `python test_db_connection.py`
- [ ] Server starts without errors: `python main.py`

---

## Need Help?

1. **Check logs:** `tail -f /var/log/fastapi.log`
2. **Run test:** `python test_db_connection.py`
3. **Verify DB:** `psql -d survey_db -c "SELECT * FROM survey_data;"`
4. **Check code:** Review `db.py` and `main.py`

---

**Last Updated:** March 24, 2026  
**Version:** 2.0.0  
**Status:** Production Ready ✅
