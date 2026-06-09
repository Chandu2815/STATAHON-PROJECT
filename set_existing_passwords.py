"""
Script to set plain_password for existing users
For development/testing purposes only
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def set_known_passwords():
    """Set known passwords for existing users"""
    db = SessionLocal()
    
    try:
        # Get all users without plain_password
        users = db.query(User).filter(User.plain_password == None).all()
        
        print(f"Found {len(users)} users without plain_password:")
        
        for user in users:
            print(f"\n{'='*50}")
            print(f"User: {user.username} (ID: {user.id})")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            
            # Set default password based on username
            if user.username == 'admin':
                plain_pass = 'password'
            else:
                plain_pass = input(f"Enter plain password for '{user.username}' (or press Enter to skip): ").strip()
                
            if plain_pass:
                user.plain_password = plain_pass
                print(f"✅ Set password for {user.username}: {plain_pass}")
            else:
                print(f"⏭️ Skipped {user.username}")
        
        db.commit()
        print(f"\n{'='*50}")
        print("✅ All passwords updated!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    set_known_passwords()
