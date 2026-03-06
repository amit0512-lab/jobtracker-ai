#!/usr/bin/env python3
"""Quick script to send OTP for email verification"""

import requests
import sys

email = sys.argv[1] if len(sys.argv) > 1 else "knnknp599@gmail.com"

print(f"\n🔐 Sending OTP to: {email}")
print("="*60)

try:
    response = requests.post(
        "http://localhost:8000/api/v1/verification/send-otp",
        json={"email": email}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['message']}")
        print(f"⏰ Expires in: {data['expires_in_seconds']} seconds")
        print("\n📧 Check your backend console for the OTP code!")
        print("   (Since SMTP is not configured, OTP is logged to console)")
    else:
        print(f"❌ Error: {response.json()}")
        
except Exception as e:
    print(f"❌ Failed: {str(e)}")
    print("\n💡 Make sure backend is running on http://localhost:8000")

print("="*60)
