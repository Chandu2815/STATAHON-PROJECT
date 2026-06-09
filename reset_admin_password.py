"""
Force reset admin password with proper bcrypt encoding
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.user import User, UserRole
import bcrypt

def reset_admin():
    db = SessionLocal()
    try:
        # Delete existing admin
        db.query(User).filter(User.username == "admin").delete()
        db.commit()
        
        # Create new admin with properly hashed password
        password = "admin123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        admin = User(
            username="admin",
            email="admin@mospi.gov.in",
            full_name="System Administrator",
            hashed_password=hashed.decode('utf-8'),
            role=UserRole.ADMIN,
            is_active=True,
            credits=999999.0
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("=" * 60)
        print("✅ ADMIN USER CREATED SUCCESSFULLY")
        print("=" * 60)
        print(f"ID: {admin.id}")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")
        print(f"Active: {admin.is_active}")
        print(f"Credits: {admin.credits}")
        print()
        print("=" * 60)
        print("LOGIN CREDENTIALS")
        print("=" * 60)
        print("Username: admin")
        print("Password: admin123")
        print("=" * 60)
        print()
        
        # Test password verification
        test_pass = "admin123"
        result = bcrypt.checkpw(test_pass.encode('utf-8'), admin.hashed_password.encode('utf-8'))
        print(f"✅ Password verification test: {result}")
        
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
