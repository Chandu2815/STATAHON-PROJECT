#!/usr/bin/env python3
"""Quick Database Connection Test"""
import sys
import os

sys.path.insert(0, '/Users/arunsudhaveni/Desktop/STATAHON PROJECT')

print('\n' + '=' * 80)
print('  DATABASE CONNECTION TEST')
print('=' * 80)

# Test 1: .env
print('\n✓ ENVIRONMENT CONFIGURATION')
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv('DATABASE_URL')
if db_url:
    print(f'  DATABASE_URL: {db_url}')
else:
    print('  ❌ No DATABASE_URL found')
    sys.exit(1)

# Test 2: SQLAlchemy
print('\n✓ SQLALCHEMY ENGINE')
try:
    from db import engine, get_db
    print('  Engine created successfully')
except Exception as e:
    print(f'  ❌ Error: {e}')
    sys.exit(1)

# Test 3: Connection
print('\n✓ DATABASE CONNECTION')
try:
    import psycopg2
    conn = psycopg2.connect(
        host='localhost', port=5432,
        database='survey_db', user='postgres',
        password='1234', connect_timeout=5
    )
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()[0]
    print(f'  Connected to PostgreSQL')
    print(f'  Version: {version.split(",")[0]}')
    
    cursor.execute('SELECT COUNT(*) FROM survey_data;')
    count = cursor.fetchone()[0]
    print(f'  survey_data table: {count:,} rows')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'  ❌ Error: {e}')
    sys.exit(1)

# Test 4: FastAPI
print('\n✓ FASTAPI APPLICATION')
try:
    from main import app
    print(f'  FastAPI app loaded')
    print(f'  Title: {app.title}')
    routes = [route.path for route in app.routes]
    print(f'  Endpoints: {len(routes)} routes')
except Exception as e:
    print(f'  ❌ Error: {e}')

print('\n' + '=' * 80)
print('  ✅ DATABASE IS FULLY CONNECTED!')
print('=' * 80)
print('\nYou can now:')
print('  1. Run: uvicorn main:app --reload')
print('  2. Open: http://localhost:8000/docs')
print('  3. Test endpoints and upload data')
print('\n' + '=' * 80 + '\n')
