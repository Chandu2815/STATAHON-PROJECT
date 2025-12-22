"""
Direct test of admin authentication in database
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.user import User
import bcrypt

def test_admin_password():
    db = SessionLocal()
    try:
        # Get admin user
        admin = db.query(User).filter(User.username == "admin").first()
        
        if not admin:
            print("❌ Admin user not found in database!")
            return
        
        print("=" * 60)
        print("ADMIN USER IN DATABASE")
        print("=" * 60)
        print(f"ID: {admin.id}")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")
        print(f"Active: {admin.is_active}")
        print(f"Credits: {admin.credits}")
        print(f"Hashed Password: {admin.hashed_password[:50]}...")
        print()
        
        # Test password verification
        test_password = "admin123"
        print(f"Testing password: '{test_password}'")
        print()
        
        # Test with bcrypt
        try:
            # Convert to bytes if needed
            password_bytes = test_password.encode('utf-8')
            hash_bytes = admin.hashed_password.encode('utf-8') if isinstance(admin.hashed_password, str) else admin.hashed_password
            
            result = bcrypt.checkpw(password_bytes, hash_bytes)
            
            if result:
                print("✅ PASSWORD VERIFICATION SUCCESSFUL!")
                print("The password 'admin123' matches the stored hash")
            else:
                print("❌ PASSWORD VERIFICATION FAILED!")
                print("The password 'admin123' does NOT match the stored hash")
                
                # Try creating a new hash and comparing
                print("\nCreating new hash for 'admin123'...")
                new_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                print(f"New hash: {new_hash}")
                
                # Update the admin password
                print("\nUpdating admin password in database...")
                admin.hashed_password = new_hash.decode('utf-8')
                db.commit()
                print("✅ Password updated successfully!")
                
                # Test again
                print("\nTesting with new hash...")
                result2 = bcrypt.checkpw(password_bytes, new_hash)
                if result2:
                    print("✅ NEW PASSWORD VERIFICATION SUCCESSFUL!")
                else:
                    print("❌ Still failing - there's a deeper issue")
                    
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_password()
