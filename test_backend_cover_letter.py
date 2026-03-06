"""
Quick test to check if backend cover letter endpoint is working
Run: python test_backend_cover_letter.py
"""

import requests

BASE_URL = "http://localhost:8000"

print("🧪 Testing Backend Cover Letter Endpoint\n")

# Test 1: Check if backend is running
print("1️⃣ Checking if backend is running...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print("✅ Backend is running\n")
    else:
        print(f"❌ Backend returned status {response.status_code}\n")
        exit(1)
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend at http://localhost:8000")
    print("   Please start the backend:")
    print("   uvicorn app.main:app --reload\n")
    exit(1)

# Test 2: Check if cover letter routes are registered
print("2️⃣ Checking if cover letter routes are registered...")
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    if "cover-letter" in response.text.lower():
        print("✅ Cover letter routes are registered\n")
    else:
        print("⚠️  Cover letter routes might not be registered")
        print("   Check app/main.py includes cover_letter router\n")
except Exception as e:
    print(f"⚠️  Could not verify routes: {e}\n")

# Test 3: Check database migration
print("3️⃣ Checking database migration...")
print("   Run: alembic current")
print("   Should show: 7ae077e9d602 (add_cover_letters_table)\n")

# Test 4: Check environment variables
print("4️⃣ Checking environment variables...")
import os
from dotenv import load_dotenv
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
if openai_key and openai_key != "your-openai-api-key-here":
    print(f"✅ OPENAI_API_KEY is set (starts with: {openai_key[:10]}...)\n")
else:
    print("⚠️  OPENAI_API_KEY not set - will use template generation\n")

print("=" * 60)
print("📋 TROUBLESHOOTING CHECKLIST")
print("=" * 60)
print("✓ Backend running: http://localhost:8000")
print("✓ Database migration applied: alembic upgrade head")
print("✓ Frontend running: http://localhost:3000")
print("✓ At least one job added with description")
print("✓ Browser console open (F12) to see errors")
print("\n💡 Common Issues:")
print("1. Backend not restarted after code changes")
print("2. Database migration not applied")
print("3. Job has no description field")
print("4. CORS issues (check backend logs)")
print("5. Type hint errors (Python 3.9 vs 3.10+)")
print("\n🔧 Quick Fix:")
print("1. Stop backend (Ctrl+C)")
print("2. Run: alembic upgrade head")
print("3. Start backend: uvicorn app.main:app --reload")
print("4. Refresh frontend (Ctrl+Shift+R)")
print("=" * 60)
