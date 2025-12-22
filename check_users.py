"""
Check users in database
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()
users = db.query(User).all()

print(f"Total users: {len(users)}")
print("="*80)

for user in users:
    print(f"ID: {user.id:3} | Username: {user.username:15} | Email: {user.email:25} | Plain: {user.plain_password}")

db.close()
