# Commands to Check Survey Data in PostgreSQL Terminal

## Basic Connection Check
```bash
# Connect to survey_db
psql -U postgres -d survey_db

# Or with password (if prompted)
psql -U postgres -d survey_db -W
```

## Once Connected (Inside psql):

### 1. CHECK CURRENT DATABASE
```sql
SELECT current_database();
```
Expected: `survey_db`

---

### 2. LIST ALL TABLES
```sql
\dt
```
or
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema='public';
```

---

### 3. CHECK SURVEY_DATA TABLE EXISTS
```sql
\d survey_data
```
Shows: Table structure with columns and indexes

---

### 4. COUNT RECORDS IN SURVEY_DATA
```sql
SELECT COUNT(*) FROM survey_data;
```
Expected: 651 records

---

### 5. VIEW SAMPLE DATA (First 5 rows)
```sql
SELECT * FROM survey_data LIMIT 5;
```

---

### 6. VIEW SPECIFIC COLUMNS
```sql
SELECT dataset_name, indicator_name, value, state, district FROM survey_data LIMIT 10;
```

---

### 7. COUNT BY STATE
```sql
SELECT state, COUNT(*) as count 
FROM survey_data 
GROUP BY state 
ORDER BY count DESC;
```

---

### 8. COUNT BY INDICATOR
```sql
SELECT indicator_name, COUNT(*) as count 
FROM survey_data 
GROUP BY indicator_name 
ORDER BY count DESC;
```

---

### 9. GET DATA FOR SPECIFIC STATE (Bihar)
```sql
SELECT * FROM survey_data WHERE state='Bihar' LIMIT 5;
```

---

### 10. GET STATISTICS
```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT dataset_name) as datasets,
    COUNT(DISTINCT category) as categories,
    COUNT(DISTINCT state) as states,
    COUNT(DISTINCT indicator_name) as indicators
FROM survey_data;
```

---

### 11. CHECK TABLE SIZE
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE tablename='survey_data';
```

---

### 12. LIST ALL INDEXES
```sql
SELECT * FROM pg_indexes WHERE tablename='survey_data';
```

---

### 13. CHECK FOR DUPLICATES
```sql
SELECT 
    dataset_name, year, indicator_name, state, district,
    COUNT(*) as count
FROM survey_data
GROUP BY dataset_name, year, indicator_name, state, district
HAVING COUNT(*) > 1;
```
(Should return empty if duplicate constraint is working)

---

## Exit psql
```sql
\q
```

---

## Quick One-Liners (From Terminal, Not Inside psql):

### Check if table exists and has data
```bash
psql -U postgres -d survey_db -c "SELECT COUNT(*) FROM survey_data;"
```

### Get all data for Bihar
```bash
psql -U postgres -d survey_db -c "SELECT * FROM survey_data WHERE state='Bihar';"
```

### Get summary statistics
```bash
psql -U postgres -d survey_db -c "SELECT 
    COUNT(*) as total,
    COUNT(DISTINCT state) as states,
    COUNT(DISTINCT indicator_name) as indicators
FROM survey_data;"
```

### Export data to CSV
```bash
psql -U postgres -d survey_db -c "COPY survey_data TO STDOUT WITH CSV HEADER;" > survey_data.csv
```

### Show table structure
```bash
psql -U postgres -d survey_db -c "\d survey_data"
```

---

## If Data Shows 0 Records:

### 1. Check if table exists
```bash
psql -U postgres -d survey_db -c "\d survey_data"
```

### 2. Verify CSV loader ran successfully
```bash
cd /Users/arunsudhaveni/STATAHON\ PROJECT
python survey-ai-app/backend/nss_survey_loader.py "data/Data in CSV (1)/DataSet.csv"
```

### 3. Check if FastAPI endpoint is running
```bash
curl http://localhost:8001/survey-data/stats
```

### 4. Manually insert test data
```bash
curl -X POST http://localhost:8001/survey-data/insert \
  -H "Content-Type: application/json" \
  -d '{
    "skip_duplicates": true,
    "records": [{
        "dataset_name": "Test",
        "category": "Test",
        "year": 2024,
        "indicator_name": "Test Indicator",
        "value": 100.0,
        "state": "Bihar",
        "district": "Patna"
    }]
  }'
```

---

## Pro Tips:

**Format output nicely:**
```bash
psql -U postgres -d survey_db -c "SELECT * FROM survey_data LIMIT 10;" | less
```

**Use expanded display:**
```sql
\x
SELECT * FROM survey_data LIMIT 1;
\x  -- toggle off
```

**Count everything:**
```bash
psql -U postgres -d survey_db << EOF
SELECT 'survey_data' as table_name, COUNT(*) as count FROM survey_data
UNION ALL
SELECT 'datasets', COUNT(*) FROM datasets
UNION ALL
SELECT 'users', COUNT(*) FROM users;
EOF
```
