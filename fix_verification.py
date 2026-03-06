"""
Quick script to set all users as verified (for development mode)
"""
from app.core.database import SessionLocal
from app.models.user import User

def fix_verification():
    db = SessionLocal()
    try:
        # Update all users to verified
        users = db.query(User).filter(User.is_verified == False).all()
        
        if not users:
            print("✓ All users are already verified")
            return
        
        for user in users:
            user.is_verified = True
            print(f"✓ Verified: {user.email}")
        
        db.commit()
        print(f"\n✓ Successfully verified {len(users)} user(s)")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_verification()
