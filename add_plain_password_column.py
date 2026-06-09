"""
Migration script to add plain_password column to users table
"""
from sqlalchemy import create_engine, text
from app.config import get_settings

settings = get_settings()

def migrate_database():
    """Add plain_password column to users table"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        # Check if column exists
        result = connection.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
        
        if 'plain_password' not in columns:
            print("Adding plain_password column to users table...")
            connection.execute(text("ALTER TABLE users ADD COLUMN plain_password VARCHAR(255)"))
            connection.commit()
            print("✅ Column added successfully!")
            print("\nNote: Existing users will have NULL plain_password.")
            print("You can reset their passwords to populate this field.")
        else:
            print("✅ plain_password column already exists!")

if __name__ == "__main__":
    migrate_database()
