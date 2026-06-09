"""
Script to check database schema and recreate original users if they don't exist
"""
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole
from app.auth import get_password_hash
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_and_restore_users():
    """Check current users and restore original ones if missing"""
    db = SessionLocal()
    
    # Original users that should exist
    original_users = {
        'testuser': {'email': 'test@example.com', 'password': 'testuser123', 'role': UserRole.PUBLIC},
        'Siri': {'email': 'siri@example.com', 'password': 'Siri123', 'role': UserRole.PUBLIC},
        'newuser123': {'email': 'newuser@example.com', 'password': 'newuser123', 'role': UserRole.PUBLIC}
    }
    
    print("="*80)
    print("CURRENT USERS IN DATABASE")
    print("="*80)
    
    existing_users = db.query(User).all()
    existing_usernames = {u.username for u in existing_users}
    
    for user in existing_users:
        print(f"ID: {user.id:3} | Username: {user.username:15} | Password: {user.plain_password or 'NULL'}")
    
    print(f"\nTotal: {len(existing_users)} users")
    
    # Check for missing original users
    missing_users = []
    for username in original_users:
        if username not in existing_usernames:
            missing_users.append(username)
    
    if missing_users:
        print("\n" + "="*80)
        print(f"FOUND {len(missing_users)} MISSING ORIGINAL USERS")
        print("="*80)
        
        for username in missing_users:
            user_data = original_users[username]
            print(f"\nRestoring: {username}")
            
            new_user = User(
                username=username,
                email=user_data['email'],
                full_name=username.title(),
                hashed_password=get_password_hash(user_data['password']),
                plain_password=user_data['password'],
                role=user_data['role'],
                is_active=True,
                credits=10.0
            )
            
            db.add(new_user)
            print(f"  ✅ Created {username} with password: {user_data['password']}")
        
        db.commit()
        print("\n" + "="*80)
        print("✅ ALL ORIGINAL USERS RESTORED!")
        print("="*80)
    else:
        print("\n✅ All original users are present!")
    
    db.close()

if __name__ == "__main__":
    check_and_restore_users()
