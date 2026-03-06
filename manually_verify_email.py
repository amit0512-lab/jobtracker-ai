#!/usr/bin/env python3
"""Manually verify an email address (for development/testing)"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get email from command line
email = sys.argv[1] if len(sys.argv) > 1 else "knnknp599@gmail.com"

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/jobtracker")

print(f"\n🔐 Manually verifying email: {email}")
print("="*60)

try:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Update user
    from sqlalchemy import text
    result = session.execute(
        text(f"UPDATE users SET is_verified = true WHERE email = :email"),
        {"email": email}
    )
    session.commit()
    
    if result.rowcount > 0:
        print(f"✅ Email verified successfully!")
        print(f"   User: {email}")
        print(f"   Status: is_verified = true")
        print(f"\n💡 You can now login!")
    else:
        print(f"❌ User not found with email: {email}")
        print(f"\n💡 Please register first at: http://localhost:3000/register")
    
    session.close()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print(f"\n💡 Make sure PostgreSQL is running and DATABASE_URL is correct")

print("="*60)
