"""
Update credits for existing demo users based on their roles
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.user import User, UserRole

def update_user_credits():
    """Update credits for demo users"""
    db = SessionLocal()
    
    try:
        # Define credits by role
        credits_by_role = {
            UserRole.PUBLIC: 10.0,
            UserRole.RESEARCHER: 100.0,
            UserRole.PREMIUM: 500.0,
            UserRole.ADMIN: 1000.0
        }
        
        # Get all users
        users = db.query(User).all()
        
        print("Updating user credits based on roles...\n")
        
        for user in users:
            new_credits = credits_by_role.get(user.role, 10.0)
            old_credits = user.credits
            user.credits = new_credits
            
            print(f"✓ {user.username} ({user.role.value}): {old_credits} → {new_credits} credits")
        
        db.commit()
        print(f"\n✓ Successfully updated {len(users)} users")
        
    except Exception as e:
        print(f"✗ Error updating credits: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_user_credits()
