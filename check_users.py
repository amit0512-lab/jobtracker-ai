"""Check what users exist in database"""
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"Found {len(users)} users:\n")
    for user in users:
        print(f"Email: {user.email}")
        print(f"  Name: {user.full_name}")
        print(f"  Verified: {user.is_verified}")
        print(f"  Active: {user.is_active}")
        print()
finally:
    db.close()
