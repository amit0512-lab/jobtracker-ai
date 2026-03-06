#!/usr/bin/env python3
"""
Comprehensive production readiness scan
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("PRODUCTION READINESS SCAN - JobTracker AI")
print("=" * 70)
print()

issues = []
warnings = []
passed = []

# 1. Check .env file
print("1. Checking environment configuration...")
if Path(".env").exists():
    with open(".env") as f:
        env_content = f.read()
        
    if "your-super-secret-key" in env_content or "change-in-production" in env_content:
        issues.append("❌ .env still has default SECRET_KEY")
    else:
        passed.append("✅ SECRET_KEY has been changed")
    
    if "your-openai-api-key" in env_content:
        warnings.append("⚠️  OpenAI API key not set (cover letters will use template)")
    else:
        passed.append("✅ OpenAI API key configured")
else:
    issues.append("❌ .env file not found")

# 2. Check .gitignore
print("2. Checking .gitignore...")
if Path(".gitignore").exists():
    with open(".gitignore") as f:
        gitignore = f.read()
    
    if ".env" in gitignore:
        passed.append("✅ .env is in .gitignore")
    else:
        issues.append("❌ .env not in .gitignore (security risk!)")
    
    if "logs/" in gitignore or "*.log" in gitignore:
        passed.append("✅ Logs are in .gitignore")
    else:
        warnings.append("⚠️  Log files not in .gitignore")
else:
    issues.append("❌ .gitignore not found")

# 3. Check CORS configuration
print("3. Checking CORS configuration...")
if Path("app/main.py").exists():
    with open("app/main.py") as f:
        main_content = f.read()
    
    # Check if wildcard is in allow_origins list
    import re
    cors_match = re.search(r'allow_origins\s*=\s*\[(.*?)\]', main_content, re.DOTALL)
    if cors_match:
        origins_str = cors_match.group(1)
        if '"*"' in origins_str or "'*'" in origins_str:
            issues.append("❌ CORS allows all origins (*) - security risk!")
        else:
            passed.append("✅ CORS properly configured (no wildcard)")
    else:
        warnings.append("⚠️  Could not parse CORS configuration")
else:
    issues.append("❌ app/main.py not found")

# 4. Check logging
print("4. Checking logging configuration...")
if Path("app/core/logging_config.py").exists():
    passed.append("✅ Logging configuration exists")
    
    if Path("logs").exists():
        passed.append("✅ Logs directory exists")
    else:
        warnings.append("⚠️  Logs directory not created yet (will be created on first run)")
else:
    issues.append("❌ Logging configuration missing")

# 5. Check file upload limits
print("5. Checking file upload limits...")
if Path("app/api/routes/resume.py").exists():
    with open("app/api/routes/resume.py") as f:
        resume_content = f.read()
    
    if "MAX_FILE_SIZE" in resume_content:
        passed.append("✅ File size limits configured")
    else:
        issues.append("❌ No file size limits")
    
    if "ALLOWED_CONTENT_TYPES" in resume_content:
        passed.append("✅ File type validation exists")
    else:
        issues.append("❌ No file type validation")
else:
    issues.append("❌ Resume routes not found")

# 6. Check rate limiting
print("6. Checking rate limiting...")
if Path("app/api/routes/cover_letter.py").exists():
    with open("app/api/routes/cover_letter.py") as f:
        cover_letter_content = f.read()
    
    if "rate_limit" in cover_letter_content:
        passed.append("✅ Rate limiting on cover letter generation")
    else:
        warnings.append("⚠️  No rate limiting on cover letter generation")
else:
    issues.append("❌ Cover letter routes not found")

# 7. Check database backups
print("7. Checking database backup...")
if Path("backup_database.py").exists():
    passed.append("✅ Database backup script exists")
    
    if Path("backups").exists():
        backup_files = list(Path("backups").glob("*.sql"))
        if backup_files:
            passed.append(f"✅ {len(backup_files)} backup(s) found")
        else:
            warnings.append("⚠️  No backups created yet")
    else:
        warnings.append("⚠️  Backups directory doesn't exist (will be created on first backup)")
else:
    issues.append("❌ Database backup script missing")

# 8. Check dependencies
print("8. Checking dependencies...")
if Path("requirements.txt").exists():
    passed.append("✅ requirements.txt exists")
else:
    issues.append("❌ requirements.txt missing")

# 9. Check database migrations
print("9. Checking database migrations...")
if Path("migrations").exists():
    migration_files = list(Path("migrations/versions").glob("*.py"))
    if migration_files:
        passed.append(f"✅ {len(migration_files)} migration(s) found")
    else:
        warnings.append("⚠️  No migrations found")
else:
    issues.append("❌ Migrations directory missing")

# 10. Check frontend build
print("10. Checking frontend...")
if Path("frontend").exists():
    if Path("frontend/package.json").exists():
        passed.append("✅ Frontend package.json exists")
    else:
        issues.append("❌ Frontend package.json missing")
    
    if Path("frontend/build").exists():
        passed.append("✅ Frontend build exists")
    else:
        warnings.append("⚠️  Frontend not built yet (run: npm run build)")
else:
    issues.append("❌ Frontend directory missing")

# 11. Check Docker configuration
print("11. Checking Docker configuration...")
if Path("docker-compose.yml").exists():
    passed.append("✅ docker-compose.yml exists")
else:
    warnings.append("⚠️  docker-compose.yml missing")

if Path("Dockerfile").exists():
    passed.append("✅ Dockerfile exists")
else:
    warnings.append("⚠️  Dockerfile missing")

# 12. Check documentation
print("12. Checking documentation...")
docs = ["README.md", "LAUNCH_CHECKLIST.md", "PRODUCTION_FIXES.md", "FIXES_APPLIED.md"]
for doc in docs:
    if Path(doc).exists():
        passed.append(f"✅ {doc} exists")
    else:
        warnings.append(f"⚠️  {doc} missing")

print()
print("=" * 70)
print("SCAN RESULTS")
print("=" * 70)
print()

if passed:
    print("✅ PASSED CHECKS:")
    for item in passed:
        print(f"  {item}")
    print()

if warnings:
    print("⚠️  WARNINGS:")
    for item in warnings:
        print(f"  {item}")
    print()

if issues:
    print("❌ CRITICAL ISSUES:")
    for item in issues:
        print(f"  {item}")
    print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"✅ Passed: {len(passed)}")
print(f"⚠️  Warnings: {len(warnings)}")
print(f"❌ Critical Issues: {len(issues)}")
print()

if issues:
    print("⚠️  FIX CRITICAL ISSUES BEFORE PRODUCTION LAUNCH!")
    sys.exit(1)
elif warnings:
    print("✅ Ready for production with minor warnings")
    sys.exit(0)
else:
    print("🎉 ALL CHECKS PASSED - PRODUCTION READY!")
    sys.exit(0)
