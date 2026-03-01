"""
Pre-Upload Verification Script
Checks if the project is ready for GitHub upload
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def check_pass(message):
    print(f"{GREEN}✅ {message}{RESET}")

def check_fail(message):
    print(f"{RED}❌ {message}{RESET}")

def check_warn(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")

def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    if Path(filepath).exists():
        check_pass(f"Found: {filepath}")
        return True
    else:
        if required:
            check_fail(f"Missing: {filepath}")
        else:
            check_warn(f"Optional file missing: {filepath}")
        return False

def check_gitignore():
    """Verify .gitignore has essential entries"""
    print_header("Checking .gitignore")
    
    if not check_file_exists(".gitignore"):
        return False
    
    with open(".gitignore", "r") as f:
        content = f.read()
    
    required_entries = [
        ".env",
        "__pycache__",
        "venv/",
        "local_storage/"
    ]
    
    all_present = True
    for entry in required_entries:
        if entry in content:
            check_pass(f"Ignoring: {entry}")
        else:
            check_fail(f"Missing in .gitignore: {entry}")
            all_present = False
    
    return all_present

def check_env_files():
    """Check environment file setup"""
    print_header("Checking Environment Files")
    
    env_exists = Path(".env").exists()
    env_example_exists = Path(".env.example").exists()
    
    if env_exists:
        check_warn(".env file exists (will be ignored by git)")
    else:
        check_warn(".env file not found (create from .env.example)")
    
    if env_example_exists:
        check_pass(".env.example exists")
    else:
        check_fail(".env.example missing - create it!")
        return False
    
    # Check if .env.example has placeholder values
    with open(".env.example", "r", encoding="utf-8") as f:
        content = f.read()
    
    dangerous_patterns = [
        "postgres:postgres@db:",  # Real DB credentials
        "AKIA",  # AWS access key prefix
    ]
    
    safe = True
    for pattern in dangerous_patterns:
        if pattern in content:
            check_fail(f"Found real credentials in .env.example: {pattern}")
            safe = False
    
    if safe:
        check_pass(".env.example has placeholder values only")
    
    return env_example_exists and safe

def check_sensitive_files():
    """Check for sensitive files that shouldn't be uploaded"""
    print_header("Checking for Sensitive Files")
    
    sensitive_files = [
        ".env",
        "*.pem",
        "*.key",
        "*.p12",
        "credentials.json",
        "secrets.yaml"
    ]
    
    found_sensitive = []
    
    for pattern in sensitive_files:
        if "*" in pattern:
            # Check pattern
            ext = pattern.split("*")[1]
            for file in Path(".").rglob(f"*{ext}"):
                if ".git" not in str(file):
                    found_sensitive.append(str(file))
        else:
            if Path(pattern).exists():
                found_sensitive.append(pattern)
    
    if found_sensitive:
        check_warn("Found sensitive files (ensure they're in .gitignore):")
        for f in found_sensitive:
            print(f"  - {f}")
    else:
        check_pass("No sensitive files found")
    
    return True

def check_required_files():
    """Check if all required files exist"""
    print_header("Checking Required Files")
    
    required_files = [
        "README.md",
        "requirements.txt",
        "docker-compose.yml",
        "Dockerfile",
        ".gitignore",
        "app/main.py",
        "frontend/app.py"
    ]
    
    all_present = True
    for filepath in required_files:
        if not check_file_exists(filepath, required=True):
            all_present = False
    
    return all_present

def check_optional_files():
    """Check for optional but recommended files"""
    print_header("Checking Optional Files")
    
    optional_files = [
        "LICENSE",
        "SETUP.md",
        ".env.example",
        "GITHUB_UPLOAD_GUIDE.md"
    ]
    
    for filepath in optional_files:
        check_file_exists(filepath, required=False)
    
    return True

def check_readme():
    """Verify README.md has essential sections"""
    print_header("Checking README.md")
    
    if not Path("README.md").exists():
        check_fail("README.md not found")
        return False
    
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    required_sections = [
        "# ",  # Title
        "## ",  # Sections
        "Features",
        "Tech Stack",
        "Quick Start",
        "Installation"
    ]
    
    all_present = True
    for section in required_sections:
        if section.lower() in content.lower():
            check_pass(f"Found section: {section}")
        else:
            check_warn(f"Missing section: {section}")
            all_present = False
    
    # Check for placeholder text
    placeholders = [
        "yourusername",
        "your-email",
        "your.email"
    ]
    
    has_placeholders = False
    for placeholder in placeholders:
        if placeholder in content:
            check_warn(f"Found placeholder in README: {placeholder}")
            has_placeholders = True
    
    if not has_placeholders:
        check_pass("No placeholders found in README")
    
    return True

def check_code_quality():
    """Basic code quality checks"""
    print_header("Checking Code Quality")
    
    # Check for common issues
    issues = []
    
    # Check for print statements in production code
    for py_file in Path("app").rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()
            if "print(" in content and "# DEBUG" not in content:
                issues.append(f"Found print() in {py_file}")
    
    if issues:
        check_warn("Found potential issues:")
        for issue in issues[:5]:  # Show first 5
            print(f"  - {issue}")
    else:
        check_pass("No obvious code issues found")
    
    return True

def check_dependencies():
    """Check if requirements.txt is present and valid"""
    print_header("Checking Dependencies")
    
    if not Path("requirements.txt").exists():
        check_fail("requirements.txt not found")
        return False
    
    with open("requirements.txt", "r") as f:
        lines = f.readlines()
    
    if len(lines) < 10:
        check_warn("requirements.txt seems incomplete (< 10 packages)")
    else:
        check_pass(f"requirements.txt has {len(lines)} dependencies")
    
    # Check for essential packages
    essential = ["fastapi", "sqlalchemy", "redis", "bcrypt", "spacy"]
    content = open("requirements.txt").read()
    
    for package in essential:
        if package in content.lower():
            check_pass(f"Found: {package}")
        else:
            check_fail(f"Missing essential package: {package}")
    
    return True

def generate_report():
    """Generate final report"""
    print_header("FINAL REPORT")
    
    checks = [
        ("Required Files", check_required_files()),
        ("Optional Files", check_optional_files()),
        (".gitignore", check_gitignore()),
        ("Environment Files", check_env_files()),
        ("Sensitive Files", check_sensitive_files()),
        ("README.md", check_readme()),
        ("Dependencies", check_dependencies()),
        ("Code Quality", check_code_quality())
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    print(f"\n{BLUE}Results: {passed}/{total} checks passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}🎉 ALL CHECKS PASSED! Ready for GitHub upload! 🎉{RESET}")
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"\n{BLUE}Next steps:{RESET}")
        print("1. Review GITHUB_UPLOAD_GUIDE.md")
        print("2. Create GitHub repository")
        print("3. Run: git init")
        print("4. Run: git add .")
        print("5. Run: git commit -m 'Initial commit'")
        print("6. Run: git remote add origin <your-repo-url>")
        print("7. Run: git push -u origin main")
    else:
        print(f"{YELLOW}{'='*60}{RESET}")
        print(f"{YELLOW}⚠️  Some checks failed. Fix them before uploading. ⚠️{RESET}")
        print(f"{YELLOW}{'='*60}{RESET}")
        print(f"\n{BLUE}Failed checks:{RESET}")
        for name, result in checks:
            if not result:
                print(f"  - {name}")
    
    print()

if __name__ == "__main__":
    print(f"{BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║          JobTracker AI - Pre-Upload Verification           ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    generate_report()
