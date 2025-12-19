"""
Create initial admin structure with multiple admin roles
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.audit import AdminAuditLog
from app.auth import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

def create_admin_hierarchy():
    """Create initial admin users with different roles"""
    db = SessionLocal()
    
    try:
        print("Creating Multi-Admin Structure...\n")
        
        admins = [
            {
                'username': 'super_admin',
                'email': 'superadmin@mospi.gov.in',
                'password': 'super123',
                'full_name': 'Super Administrator',
                'role': UserRole.SUPER_ADMIN,
                'credits': 999999.0,
                'description': 'Full system control'
            },
            {
                'username': 'data_admin',
                'email': 'dataadmin@mospi.gov.in',
                'password': 'data123',
                'full_name': 'Data Manager',
                'role': UserRole.DATA_ADMIN,
                'credits': 999999.0,
                'description': 'Manages datasets and uploads'
            },
            {
                'username': 'user_admin',
                'email': 'useradmin@mospi.gov.in',
                'password': 'user123',
                'full_name': 'User Manager',
                'role': UserRole.USER_ADMIN,
                'credits': 999999.0,
                'description': 'Manages user accounts'
            },
            {
                'username': 'support_admin',
                'email': 'support@mospi.gov.in',
                'password': 'support123',
                'full_name': 'Support Staff',
                'role': UserRole.SUPPORT_ADMIN,
                'credits': 999999.0,
                'description': 'View-only support access'
            },
        ]
        
        # Update existing 'admin' user to super_admin
        existing_admin = db.query(User).filter(User.username == 'admin').first()
        if existing_admin:
            existing_admin.role = UserRole.SUPER_ADMIN
            existing_admin.credits = 999999.0
            print(f"✓ Updated existing 'admin' to SUPER_ADMIN role")
        
        # Create new admin users
        for admin_data in admins:
            existing = db.query(User).filter(User.username == admin_data['username']).first()
            
            if not existing:
                admin_user = User(
                    username=admin_data['username'],
                    email=admin_data['email'],
                    hashed_password=get_password_hash(admin_data['password']),
                    full_name=admin_data['full_name'],
                    role=admin_data['role'],
                    is_active=True,
                    credits=admin_data['credits']
                )
                db.add(admin_user)
                print(f"✓ Created: {admin_data['username']} ({admin_data['role'].value})")
                print(f"  Password: {admin_data['password']}")
                print(f"  Role: {admin_data['description']}\n")
            else:
                print(f"⚠ {admin_data['username']} already exists\n")
        
        db.commit()
        
        print("\n" + "="*60)
        print("ADMIN HIERARCHY CREATED")
        print("="*60 + "\n")
        
        print("📋 Admin Access Credentials:\n")
        print("1. SUPER ADMIN (Full Control)")
        print("   URL: http://localhost:8080/admin/login")
        print("   Username: super_admin | Password: super123")
        print("   OR")
        print("   Username: admin | Password: admin123\n")
        
        print("2. DATA ADMIN (Dataset Management)")
        print("   URL: http://localhost:8080/admin/login")
        print("   Username: data_admin | Password: data123\n")
        
        print("3. USER ADMIN (User Management)")
        print("   URL: http://localhost:8080/admin/login")
        print("   Username: user_admin | Password: user123\n")
        
        print("4. SUPPORT ADMIN (View Only)")
        print("   URL: http://localhost:8080/admin/login")
        print("   Username: support_admin | Password: support123\n")
        
        print("="*60)
        
        # Show permission matrix
        print("\n📊 Permission Matrix:\n")
        print("Permission              | Super | Data | User | Support")
        print("-" * 60)
        print("Manage Users           |   ✓   |  ✗   |  ✓   |   ✗")
        print("Manage Admins          |   ✓   |  ✗   |  ✗   |   ✗")
        print("Manage Datasets        |   ✓   |  ✓   |  ✗   |   ✗")
        print("Upload Datasets        |   ✓   |  ✓   |  ✗   |   ✗")
        print("Delete Users           |   ✓   |  ✗   |  ✓   |   ✗")
        print("View Audit Logs        |   ✓   |  ✗   |  ✓   |   ✗")
        print("System Config          |   ✓   |  ✗   |  ✗   |   ✗")
        print("View All Data          |   ✓   |  ✓   |  ✗   |   ✓")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_hierarchy()
