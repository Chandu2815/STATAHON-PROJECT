"""
Complete authentication debugging - check every step
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.user import User
import bcrypt

def debug_complete_auth():
    db = SessionLocal()
    try:
        print("=" * 70)
        print("STEP 1: Check Database Connection")
        print("=" * 70)
        
        # Get admin from database
        admin = db.query(User).filter(User.username == "admin").first()
        
        if not admin:
            print("❌ PROBLEM: Admin user not found in database!")
            return
        
        print("✅ Admin user found in database")
        print(f"   ID: {admin.id}")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Is Active: {admin.is_active}")
        print(f"   Hash (first 50 chars): {admin.hashed_password[:50]}")
        print(f"   Hash type: {type(admin.hashed_password)}")
        print()
        
        print("=" * 70)
        print("STEP 2: Test Password Verification (Direct bcrypt)")
        print("=" * 70)
        
        test_password = "password"
        print(f"Testing password: '{test_password}'")
        
        # Test with bcrypt directly
        try:
            password_bytes = test_password.encode('utf-8')
            hash_bytes = admin.hashed_password.encode('utf-8') if isinstance(admin.hashed_password, str) else admin.hashed_password
            
            print(f"   Password bytes length: {len(password_bytes)}")
            print(f"   Hash bytes length: {len(hash_bytes)}")
            print(f"   Hash starts with: {hash_bytes[:10]}")
            
            result = bcrypt.checkpw(password_bytes, hash_bytes)
            print(f"   ✅ Bcrypt verification result: {result}")
        except Exception as e:
            print(f"   ❌ Bcrypt verification error: {e}")
            import traceback
            traceback.print_exc()
            
        print()
        
        print("=" * 70)
        print("STEP 3: Test verify_password Function from auth.py")
        print("=" * 70)
        
        # Import and test the actual verify_password function
        from app.auth import verify_password
        
        try:
            result = verify_password(test_password, admin.hashed_password)
            print(f"   verify_password() result: {result}")
            if result:
                print("   ✅ auth.verify_password() works correctly")
            else:
                print("   ❌ PROBLEM: auth.verify_password() returned False!")
        except Exception as e:
            print(f"   ❌ PROBLEM: auth.verify_password() raised error: {e}")
            import traceback
            traceback.print_exc()
            
        print()
        
        print("=" * 70)
        print("STEP 4: Test Login Endpoint Logic")
        print("=" * 70)
        
        # Simulate the login endpoint logic
        form_username = "admin"
        form_password = "password"
        
        print(f"   Looking for user with username: '{form_username}'")
        
        user = db.query(User).filter(User.username == form_username).first()
        
        if not user:
            print(f"   ❌ PROBLEM: User not found with username '{form_username}'")
        else:
            print(f"   ✅ User found: {user.username}")
            
            print(f"   Verifying password...")
            pwd_check = verify_password(form_password, user.hashed_password)
            print(f"   Password check result: {pwd_check}")
            
            if not pwd_check:
                print(f"   ❌ PROBLEM: Password verification failed in login flow!")
                print(f"      Input password: '{form_password}'")
                print(f"      Stored hash: {user.hashed_password[:50]}...")
            else:
                print(f"   ✅ Login flow would succeed!")
                
            if not user.is_active:
                print(f"   ❌ PROBLEM: User is inactive!")
            else:
                print(f"   ✅ User is active")
                
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        
        if admin and result and verify_password(test_password, admin.hashed_password):
            print("✅ ALL CHECKS PASSED!")
            print()
            print("Your admin credentials should be:")
            print("   Username: admin")
            print("   Password: password")
            print()
            print("Try logging in at: http://127.0.0.1:8889/admin/login")
        else:
            print("❌ THERE ARE PROBLEMS IN THE AUTHENTICATION CHAIN")
            print("   Check the errors above to identify the issue")
            
        print("=" * 70)
        
    finally:
        db.close()

if __name__ == "__main__":
    debug_complete_auth()
