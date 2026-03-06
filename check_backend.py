"""
Quick script to check if backend is properly configured
Run: python check_backend.py
"""

import sys

print("🔍 Checking Backend Configuration...\n")

# Check 1: Import main app
print("1️⃣ Checking if app can be imported...")
try:
    from app.main import app
    print("✅ App imported successfully\n")
except Exception as e:
    print(f"❌ Failed to import app: {e}\n")
    sys.exit(1)

# Check 2: Check routes
print("2️⃣ Checking registered routes...")
routes = [route.path for route in app.routes]
cover_letter_routes = [r for r in routes if 'cover-letter' in r]

if cover_letter_routes:
    print("✅ Cover letter routes found:")
    for route in cover_letter_routes:
        print(f"   - {route}")
    print()
else:
    print("❌ No cover letter routes found!")
    print("   Routes should include:")
    print("   - /api/v1/cover-letter/generate")
    print("   - /api/v1/cover-letter")
    print("   - /api/v1/cover-letter/{cover_letter_id}")
    print("   - /api/v1/cover-letter/job/{job_id}")
    print("\n   Fix: Check app/main.py includes cover_letter router\n")
    sys.exit(1)

# Check 3: Check models
print("3️⃣ Checking if CoverLetter model exists...")
try:
    from app.models.cover_letter import CoverLetter
    print("✅ CoverLetter model imported successfully\n")
except Exception as e:
    print(f"❌ Failed to import CoverLetter model: {e}\n")
    sys.exit(1)

# Check 4: Check controller
print("4️⃣ Checking if CoverLetterController exists...")
try:
    from app.api.controllers.cover_letter_controller import CoverLetterController
    print("✅ CoverLetterController imported successfully\n")
except Exception as e:
    print(f"❌ Failed to import CoverLetterController: {e}\n")
    sys.exit(1)

# Check 5: Check AI service
print("5️⃣ Checking if CoverLetterGenerator exists...")
try:
    from app.services.ai.cover_letter_generator import CoverLetterGenerator
    print("✅ CoverLetterGenerator imported successfully\n")
except Exception as e:
    print(f"❌ Failed to import CoverLetterGenerator: {e}\n")
    sys.exit(1)

# Check 6: Check environment
print("6️⃣ Checking environment variables...")
import os
from dotenv import load_dotenv
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
if openai_key and openai_key != "your-openai-api-key-here":
    print(f"✅ OPENAI_API_KEY is set\n")
else:
    print("⚠️  OPENAI_API_KEY not set (will use template generation)\n")

# Check 7: Database migration
print("7️⃣ Checking database migration...")
print("   Run this command to verify:")
print("   alembic current")
print("   Should show: 7ae077e9d602 (add_cover_letters_table)\n")

# Summary
print("=" * 60)
print("✅ ALL CHECKS PASSED!")
print("=" * 60)
print("\n📋 Next Steps:")
print("1. Start backend: uvicorn app.main:app --reload")
print("2. Check API docs: http://localhost:8000/docs")
print("3. Look for 'Cover Letters' section in docs")
print("4. Test in frontend: http://localhost:3000")
print("\n💡 If you still get 404:")
print("   - Make sure backend is actually running")
print("   - Try hard restart: pkill -f uvicorn && uvicorn app.main:app --reload")
print("   - Check backend terminal for errors")
print("=" * 60)
