#!/usr/bin/env python3
"""Test registration endpoint"""

import requests

data = {
    "email": "newuser123@example.com",
    "password": "admin123",
    "full_name": "New User"
}

print("\n🔐 Testing Registration")
print("="*60)
print(f"Email: {data['email']}")
print(f"Name: {data['full_name']}")
print("="*60)

try:
    response = requests.post(
        "http://localhost:8000/api/v1/auth/register",
        json=data
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("="*60)
