"""
Script to auto-set plain_password for existing users with their usernames as passwords
For development/testing purposes only
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def auto_set_passwords():
    """Automatically set plain_password = username for existing users"""
    db = SessionLocal()
    
    try:
        # Get all users (including those with NULL plain_password)
        users = db.query(User).all()
        users_to_update = [u for u in users if not u.plain_password]
        
        print(f"Found {len(users_to_update)} users needing password update")
        print("="*60)
        
        # Special cases
        password_map = {
            'admin': 'password',
            'testuser': 'testuser123',
            'Siri': 'Siri123',
            'newuser123': 'newuser123'
        }
        
        for user in users_to_update:
            # Use mapped password or default to 'password123'
            plain_pass = password_map.get(user.username, 'password123')
            user.plain_password = plain_pass
            print(f"✅ {user.username:20} -> Password: {plain_pass}")
        
        db.commit()
        print("="*60)
        print(f"✅ Updated {len(users_to_update)} users!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    auto_set_passwords()
