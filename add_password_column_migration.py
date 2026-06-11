"""Add password column to users table (PostgreSQL-only)"""
from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        conn.execute(text('ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS password VARCHAR(255);'))
        print("✅ Password column ensured successfully!")
except Exception as e:
    print(f"❌ Error performing migration: {e}")
