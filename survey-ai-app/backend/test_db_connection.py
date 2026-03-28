#!/usr/bin/env python3
"""
Database Connection Test Script
Tests connection to VPS PostgreSQL database and displays configuration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
backend_dir = Path(__file__).parent
env_file = backend_dir / ".env"

if not env_file.exists():
    logger.error(f"❌ .env file not found at {env_file}")
    sys.exit(1)

load_dotenv(env_file, verbose=True)

# Read configuration
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print("\n" + "="*70)
print("DATABASE CONNECTION CONFIGURATION TEST")
print("="*70 + "\n")

# Validate configuration
print("📋 Checking environment variables...")
config_valid = True

if DB_HOST:
    print(f"  ✅ DB_HOST: {DB_HOST}")
else:
    print(f"  ❌ DB_HOST: NOT SET")
    config_valid = False

if DB_NAME:
    print(f"  ✅ DB_NAME: {DB_NAME}")
else:
    print(f"  ❌ DB_NAME: NOT SET")
    config_valid = False

if DB_USER:
    print(f"  ✅ DB_USER: {DB_USER}")
else:
    print(f"  ❌ DB_USER: NOT SET")
    config_valid = False

if DB_PASSWORD:
    print(f"  ✅ DB_PASSWORD: {'*' * len(DB_PASSWORD)}")
else:
    print(f"  ❌ DB_PASSWORD: NOT SET")
    config_valid = False

print(f"  ✅ DB_PORT: {DB_PORT}")

if not config_valid:
    print("\n❌ Configuration is incomplete. Please update .env file.\n")
    sys.exit(1)

print("\n" + "-"*70)
print("🔄 Testing Database Connection...")
print("-"*70 + "\n")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    # Connection attempt
    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}...")
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=10
    )
    
    print(f"✅ Successfully connected to {DB_HOST}:{DB_PORT}\n")
    
    # Get server information
    cur = conn.cursor()
    
    # PostgreSQL version
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✅ PostgreSQL Version:")
    print(f"   {version[0]}\n")
    
    # Database stats
    cur.execute("""
        SELECT datname, pg_size_pretty(pg_database_size(datname)) as size
        FROM pg_database
        WHERE datname = %s;
    """, (DB_NAME,))
    db_info = cur.fetchone()
    print(f"✅ Database: {db_info[0]}")
    print(f"   Size: {db_info[1]}\n")
    
    # Table count
    cur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'public';
    """)
    table_count = cur.fetchone()[0]
    print(f"✅ Tables in public schema: {table_count}\n")
    
    # List tables
    cur.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)
    tables = cur.fetchall()
    print(f"✅ Tables:")
    for table in tables:
        print(f"   - {table[0]}")
    
    print("\n" + "="*70)
    print("✅ ALL DATABASE CONNECTION TESTS PASSED!")
    print("="*70)
    print(f"\nConfiguration Summary:")
    print(f"  Host:     {DB_HOST}")
    print(f"  Port:     {DB_PORT}")
    print(f"  Database: {DB_NAME}")
    print(f"  User:     {DB_USER}")
    print(f"  URL:      postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("\n✅ Backend will connect to this VPS database (not localhost)\n")
    
    cur.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"\n❌ OPERATIONAL ERROR (Connection failed):")
    print(f"   {str(e)}\n")
    print("   Possible causes:")
    print("   - VPS server is down or unreachable")
    print("   - Network/firewall blocking connection")
    print("   - Credentials are incorrect")
    print("   - Database doesn't exist\n")
    sys.exit(1)
    
except psycopg2.DatabaseError as e:
    print(f"\n❌ DATABASE ERROR:")
    print(f"   {str(e)}\n")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR:")
    print(f"   {str(e)}\n")
    sys.exit(1)
