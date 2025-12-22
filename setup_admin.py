"""
Setup and display admin credentials
"""
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.auth import get_password_hash

def setup_admin():
    """Create or reset admin user"""
    print("=" * 60)
    print("ADMIN USER SETUP")
    print("=" * 60)
    
    db = SessionLocal()
    
    # Check if admin exists
    admin = db.query(User).filter(
        (User.username == "admin") | (User.role == UserRole.ADMIN)
    ).first()
    
    admin_password = "password"
    
    if admin:
        print(f"\nFound existing admin user: {admin.username}")
        print("Resetting password...")
        
        # Reset password
        admin.hashed_password = get_password_hash(admin_password)
        admin.plain_password = admin_password  # Store plain password
        admin.role = UserRole.ADMIN
        admin.is_active = True
        admin.credits = 999999.0
        
        db.commit()
        db.refresh(admin)
        
        print("[SUCCESS] Admin password reset!")
    else:
        print("\nNo admin user found. Creating new admin...")
        
        # Create new admin
        admin = User(
            username="admin",
            email="admin@mospi.gov.in",
            full_name="System Administrator",
            hashed_password=get_password_hash(admin_password),
            plain_password=admin_password,  # Store plain password
            role=UserRole.ADMIN,
            credits=999999.0,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("[SUCCESS] Admin user created!")
    
    print(f"\nAdmin Details:")
    print(f"  ID: {admin.id}")
    print(f"  Username: {admin.username}")
    print(f"  Email: {admin.email}")
    print(f"  Role: {admin.role.value}")
    print(f"  Credits: {admin.credits}")
    print(f"  Active: {admin.is_active}")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("ADMIN LOGIN CREDENTIALS")
    print("=" * 60)
    print(f"  Username: admin")
    print(f"  Password: {admin_password}")
    print("=" * 60)
    print("\nUse these credentials to log in at:")
    print("  http://127.0.0.1:8888/admin/login")
    print("=" * 60)

if __name__ == "__main__":
    setup_admin()
