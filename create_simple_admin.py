"""
Create admin with simple password "password"
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.user import User, UserRole
import bcrypt

def create_test_admin():
    db = SessionLocal()
    try:
        # Delete existing admin
        db.query(User).filter(User.username == "admin").delete()
        db.commit()
        
        # Create admin with simple password "password"
        password = "password"
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
        
        print("✅ Admin created with password: password")
        print(f"Username: {admin.username}")
        print(f"Password: password")
        
        # Test verification
        test1 = bcrypt.checkpw(b"password", admin.hashed_password.encode('utf-8'))
        print(f"\nPassword test: {test1}")
        
    finally:
        db.close()

if __name__ == "__main__":
    create_test_admin()
