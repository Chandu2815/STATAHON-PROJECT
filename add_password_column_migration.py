"""
Add password column to users table
"""
from sqlalchemy import create_engine, text

# Create engine
engine = create_engine('sqlite:///./mospi_dpi.db')

try:
    with engine.connect() as conn:
        # Add password column
        conn.execute(text('ALTER TABLE users ADD COLUMN password VARCHAR(255);'))
        conn.commit()
        print("✅ Password column added successfully!")
except Exception as e:
    if "duplicate column name" in str(e).lower():
        print("ℹ️  Password column already exists")
    else:
        print(f"❌ Error: {e}")
