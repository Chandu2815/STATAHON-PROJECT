"""
Update existing users to set their password field
"""
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()

# Set password for existing users
users = db.query(User).all()

for user in users:
    if not user.password:
        # Try common defaults or set a generic one
        if user.username == "admin":
            user.password = "password"
        elif user.username == "Vibe":
            user.password = "password123"  # You may want to set actual passwords
        else:
            user.password = "password123"  # Default password
            
print(f"✅ Updated {len(users)} users with password field")

db.commit()
db.close()
