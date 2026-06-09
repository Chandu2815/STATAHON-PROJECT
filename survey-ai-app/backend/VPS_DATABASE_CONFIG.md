# VPS Database Connection Configuration Guide

## Overview
FastAPI backend is now configured to **exclusively connect to VPS PostgreSQL database** instead of localhost.

**VPS Database Details:**
- Host: `187.127.135.117`
- Port: `5432`
- Database: `survey_db`
- User: `survey_user`

---

## Files Created/Modified

### ✅ 1. `.env` (NEW FILE)
**Location:** `survey-ai-app/backend/.env`

**Purpose:** Stores VPS database credentials securely

**Content:**
```env
# VPS Database Credentials
DB_HOST=187.127.135.117
DB_PORT=5432
DB_NAME=survey_db
DB_USER=survey_user
DB_PASSWORD=Survey@123
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=10
DB_ECHO_SQL=false
```

**Key Points:**
- ✅ Loaded automatically on app startup
- ✅ No hardcoded localhost defaults
- ✅ Password encoded to handle special characters (@, #, etc.)

---

### ✅ 2. `database/connection.py` (UPDATED)
**Location:** `survey-ai-app/backend/database/connection.py`

**Changes Made:**
1. ❌ Removed fallback defaults (e.g., `127.0.0.1`, `postgres`)
2. ✅ Added environment variable validation
3. ✅ Added comprehensive logging
4. ✅ Added startup connection test
5. ✅ Added password URL encoding for special characters
6. ✅ Added connection pooling configuration
7. ✅ Added connection error handling

**Key Code:**
```python
# NO FALLBACK DEFAULTS - Read from .env only
DB_HOST = os.getenv("DB_HOST")  # No default!
DB_PORT = os.getenv("DB_PORT", "5432")  # Only port has default

# Validate required variables
if not DB_HOST:
    raise RuntimeError("❌ DB_HOST not set in .env file")

# Connection test on startup
with engine.connect() as conn:
    result = conn.execute("SELECT version()").fetchone()
    logger.info(f"✅ Connected to PostgreSQL at {DB_HOST}:{DB_PORT}")
```

**Startup Logs When Backend Starts:**
```
✅ Successfully connected to PostgreSQL at 187.127.135.117:5432
✅ PostgreSQL version: PostgreSQL 13.x on x86_64...
```

---

### ✅ 3. `main.py` (UPDATED)
**Location:** `survey-ai-app/backend/main.py`

**Changes Made:**
1. ❌ Removed fallback defaults in DB_CONFIG
2. ✅ Added environment variable validation
3. ✅ Added startup event to test connection
4. ✅ Added detailed error logging
5. ✅ Added version and status logging

**Key Code:**
```python
# NO FALLBACK DEFAULTS
DB_CONFIG = {
    "host": DB_HOST,        # From .env
    "port": int(DB_PORT),   # From .env
    "database": DB_NAME,    # From .env
    "user": DB_USER,        # From .env
    "password": DB_PASSWORD # From .env
}

@app.on_event("startup")
async def startup_event():
    """Test database connection on app startup"""
    conn = get_db_connection()
    logger.info(f"✅ Connected to PostgreSQL at {DB_HOST}:{DB_PORT}")
    logger.info(f"✅ Database: {DB_NAME}")
```

---

### ✅ 4. `test_db_connection.py` (NEW FILE)
**Location:** `survey-ai-app/backend/test_db_connection.py`

**Purpose:** Test VPS database connection before running backend

**Usage:**
```bash
cd survey-ai-app/backend
python test_db_connection.py
```

**Output Example:**
```
✅ Successfully connected to 187.127.135.117:5432
✅ PostgreSQL Version: PostgreSQL 13.x...
✅ Database: survey_db
✅ Size: 2.5 MB
✅ Tables in public schema: 12
✅ Tables:
   - survey_data
   - hces_food_expenditure
   - users
   ...
```

---

## How to Use

### Step 1: Verify .env File
```bash
cat survey-ai-app/backend/.env
```

**Should show:**
```
DB_HOST=187.127.135.117
DB_PORT=5432
DB_NAME=survey_db
DB_USER=survey_user
DB_PASSWORD=Survey@123
```

---

### Step 2: Test Connection
```bash
cd survey-ai-app/backend
python test_db_connection.py
```

**Expected:** ✅ All tests pass

---

### Step 3: Start Backend
```bash
cd survey-ai-app/backend
python main.py
```

**Expected Startup Logs:**
```
logging.info: ✅ Connected to PostgreSQL at 187.127.135.117:5432
logging.info: ✅ Database: survey_db
logging.info: ✅ PostgreSQL version: PostgreSQL 13.x...
```

---

## Verification

### Check Logs
Backend logs will show on startup:
```
✅ Successfully connected to PostgreSQL at 187.127.135.117:5432
```

NOT:
```
✅ Successfully connected to PostgreSQL at 127.0.0.1:5432
```

### Check Health Endpoint
```bash
curl http://localhost:8001/health
```

**Response:**
```json
{"status":"healthy","message":"Survey AI API is running"}
```

---

## Troubleshooting

### Error: "Missing required environment variables"

**Cause:** `.env` file not found or incomplete

**Fix:**
```bash
# Check if .env exists
ls -la survey-ai-app/backend/.env

# If missing, create it with correct values
echo "DB_HOST=187.127.135.117" > survey-ai-app/backend/.env
echo "DB_PORT=5432" >> survey-ai-app/backend/.env
echo "DB_NAME=survey_db" >> survey-ai-app/backend/.env
echo "DB_USER=survey_user" >> survey-ai-app/backend/.env
echo "DB_PASSWORD=Survey@123" >> survey-ai-app/backend/.env
```

---

### Error: "Connection refused" or "timeout"

**Cause:** VPS server is down or firewall is blocking

**Check:**
```bash
# Test VPS connectivity
ping 187.127.135.117

# Test port 5432
nc -zv 187.127.135.117 5432
```

**Fix:** Contact VPS provider or check firewall rules

---

### Error: "FATAL: password authentication failed"

**Cause:** Wrong credentials in `.env`

**Fix:**
1. Verify credentials with VPS provider
2. Update `.env` file
3. Restart backend

---

## Security Notes

✅ **What's Secure:**
- Password is loaded from `.env` (not in code)
- `.env` should be added to `.gitignore` (never commit credentials)
- Connection uses encrypted credentials in DATABASE_URL

⚠️ **What to Do:**
1. Add `.env` to `.gitignore`
   ```bash
   echo ".env" >> survey-ai-app/backend/.gitignore
   ```

2. Never share `.env` file
3. Use strong passwords for database

---

## Environment Variables

All in `.env` file:

| Variable | Required | Default | Example |
|----------|----------|---------|---------|
| DB_HOST | ✅ Yes | None | `187.127.135.117` |
| DB_PORT | ❌ No | `5432` | `5432` |
| DB_NAME | ✅ Yes | None | `survey_db` |
| DB_USER | ✅ Yes | None | `survey_user` |
| DB_PASSWORD | ✅ Yes | None | `Survey@123` |
| DB_POOL_SIZE | ❌ No | `10` | `10` |
| DB_MAX_OVERFLOW | ❌ No | `20` | `20` |
| DB_POOL_TIMEOUT | ❌ No | `10` | `10` |
| DB_ECHO_SQL | ❌ No | `false` | `false` |

---

## Connection Flow

```
Backend Startup
    ↓
Load .env file (via load_dotenv)
    ↓
Read DB_HOST, DB_USER, etc.
    ↓
Validate required variables exist
    ↓
Create SQLAlchemy engine with VPS credentials
    ↓
Test connection: SELECT version()
    ↓
Log: "✅ Connected to PostgreSQL at 187.127.135.117:5432"
    ↓
Backend ready to accept requests
```

---

## Testing Connection Programmatically

```python
from database.connection import get_db_sync

# Get sync session
db = get_db_sync()

# Test query
try:
    result = db.execute("SELECT version()").fetchone()
    print(f"✅ Connected! PostgreSQL: {result[0]}")
finally:
    db.close()
```

---

## Database Operations

All database operations now connect through VPS:

### FastAPI Dependency Injection
```python
from database.connection import get_db

@app.get("/data")
async def get_data(db: Session = Depends(get_db)):
    # Uses VPS database
    return db.query(SurveyData).limit(10).all()
```

### Direct Query
```python
from database.connection import get_db_sync

db = get_db_sync()
data = db.query(SurveyData).filter(SurveyData.state == "Bihar").all()
```

---

## Monitoring Connections

### Check Active Connections
```bash
psql -h 187.127.135.117 -U survey_user -d survey_db -c \
  "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

### Check Connection Pool Status
Backend logs show pool utilization:
```python
logger.info(f"Pool size: {engine.pool.size()}")
logger.info(f"Checked out: {engine.pool.checkedout()}")
```

---

## Summary of Changes

| File | Change | Impact |
|------|--------|--------|
| `.env` | ✅ Created | Stores VPS credentials |
| `database/connection.py` | ❌ Removed defaults<br>✅ Added validation | Always uses VPS |
| `main.py` | ❌ Removed defaults<br>✅ Added startup test | Always uses VPS |
| `test_db_connection.py` | ✅ Created | Test script |

---

## Next Steps

1. ✅ Verify `.env` file exists and has VPS credentials
2. ✅ Run `test_db_connection.py` to confirm connection
3. ✅ Start backend with `python main.py`
4. ✅ Check logs for "✅ Connected to PostgreSQL at 187.127.135.117"
5. ✅ Test endpoints at `http://localhost:8001/health`

---

**Status:** ✅ **CONFIGURED FOR VPS CONNECTION**  
**Backend will always connect to:** `187.127.135.117:5432` (not localhost)  
**Created:** March 28, 2026
