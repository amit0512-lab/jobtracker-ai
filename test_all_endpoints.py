import requests
import json
from typing import Optional

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api/v1"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

test_results = {"passed": 0, "failed": 0}


def log_test(name: str, passed: bool, details: str = ""):
    if passed:
        print(f"{GREEN}✅ PASS{RESET} - {name}")
        test_results["passed"] += 1
    else:
        print(f"{RED}❌ FAIL{RESET} - {name}")
        if details:
            print(f"   {RED}{details}{RESET}")
        test_results["failed"] += 1


def test_health():
    """Test health endpoint"""
    print(f"\n{BLUE}=== Testing Health Endpoint ==={RESET}")
    try:
        response = requests.get(f"{BASE_URL}/health")
        log_test("GET /health", response.status_code == 200)
        print(f"   Response: {response.json()}")
    except Exception as e:
        log_test("GET /health", False, str(e))


def test_register_success():
    """Test successful registration"""
    print(f"\n{BLUE}=== Testing Registration ==={RESET}")
    data = {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "password123"
    }
    try:
        response = requests.post(f"{API_URL}/auth/register", json=data)
        success = response.status_code == 201
        log_test("POST /auth/register - Success", success)
        if success:
            user = response.json()
            print(f"   User ID: {user['id']}")
            print(f"   Email: {user['email']}")
            return user
    except Exception as e:
        log_test("POST /auth/register - Success", False, str(e))
    return None


def test_register_duplicate():
    """Test registration with duplicate email"""
    data = {
        "email": "newuser@example.com",
        "full_name": "Duplicate User",
        "password": "password123"
    }
    try:
        response = requests.post(f"{API_URL}/auth/register", json=data)
        success = response.status_code == 400
        log_test("POST /auth/register - Duplicate Email", success)
        if success:
            print(f"   Error: {response.json()['detail']}")
    except Exception as e:
        log_test("POST /auth/register - Duplicate Email", False, str(e))


def test_register_invalid_password():
    """Test registration with short password"""
    data = {
        "email": "short@example.com",
        "full_name": "Short Pass",
        "password": "123"
    }
    try:
        response = requests.post(f"{API_URL}/auth/register", json=data)
        success = response.status_code == 422
        log_test("POST /auth/register - Short Password", success)
        if success:
            print(f"   Validation error caught")
    except Exception as e:
        log_test("POST /auth/register - Short Password", False, str(e))


def test_register_invalid_email():
    """Test registration with invalid email"""
    data = {
        "email": "notanemail",
        "full_name": "Bad Email",
        "password": "password123"
    }
    try:
        response = requests.post(f"{API_URL}/auth/register", json=data)
        success = response.status_code == 422
        log_test("POST /auth/register - Invalid Email", success)
    except Exception as e:
        log_test("POST /auth/register - Invalid Email", False, str(e))


def test_login_success():
    """Test successful login"""
    print(f"\n{BLUE}=== Testing Login ==={RESET}")
    data = {
        "email": "newuser@example.com",
        "password": "password123"
    }
    try:
        response = requests.post(f"{API_URL}/auth/login", json=data)
        success = response.status_code == 200
        log_test("POST /auth/login - Success", success)
        if success:
            tokens = response.json()
            print(f"   Access Token: {tokens['access_token'][:50]}...")
            print(f"   Refresh Token: {tokens['refresh_token'][:50]}...")
            return tokens
    except Exception as e:
        log_test("POST /auth/login - Success", False, str(e))
    return None


def test_login_wrong_password():
    """Test login with wrong password"""
    data = {
        "email": "newuser@example.com",
        "password": "wrongpassword"
    }
    try:
        response = requests.post(f"{API_URL}/auth/login", json=data)
        success = response.status_code == 401
        log_test("POST /auth/login - Wrong Password", success)
        if success:
            print(f"   Error: {response.json()['detail']}")
    except Exception as e:
        log_test("POST /auth/login - Wrong Password", False, str(e))


def test_login_nonexistent_user():
    """Test login with non-existent email"""
    data = {
        "email": "doesnotexist@example.com",
        "password": "password123"
    }
    try:
        response = requests.post(f"{API_URL}/auth/login", json=data)
        success = response.status_code == 401
        log_test("POST /auth/login - Non-existent User", success)
    except Exception as e:
        log_test("POST /auth/login - Non-existent User", False, str(e))


def test_get_profile(access_token: str):
    """Test getting user profile"""
    print(f"\n{BLUE}=== Testing Profile ==={RESET}")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{API_URL}/auth/me", headers=headers)
        success = response.status_code == 200
        log_test("GET /auth/me - Success", success)
        if success:
            user = response.json()
            print(f"   Email: {user['email']}")
            print(f"   Name: {user['full_name']}")
    except Exception as e:
        log_test("GET /auth/me - Success", False, str(e))


def test_get_profile_no_token():
    """Test getting profile without token"""
    try:
        response = requests.get(f"{API_URL}/auth/me")
        success = response.status_code == 403
        log_test("GET /auth/me - No Token", success)
    except Exception as e:
        log_test("GET /auth/me - No Token", False, str(e))


def test_get_profile_invalid_token():
    """Test getting profile with invalid token"""
    headers = {"Authorization": "Bearer invalid_token_here"}
    try:
        response = requests.get(f"{API_URL}/auth/me", headers=headers)
        success = response.status_code == 401
        log_test("GET /auth/me - Invalid Token", success)
    except Exception as e:
        log_test("GET /auth/me - Invalid Token", False, str(e))


def test_refresh_token(refresh_token: str):
    """Test refreshing access token"""
    print(f"\n{BLUE}=== Testing Token Refresh ==={RESET}")
    data = {"refresh_token": refresh_token}
    try:
        response = requests.post(f"{API_URL}/auth/refresh", json=data)
        success = response.status_code == 200
        log_test("POST /auth/refresh - Success", success)
        if success:
            tokens = response.json()
            print(f"   New Access Token: {tokens['access_token'][:50]}...")
            return tokens
    except Exception as e:
        log_test("POST /auth/refresh - Success", False, str(e))
    return None


def test_refresh_invalid_token():
    """Test refresh with invalid token"""
    data = {"refresh_token": "invalid_refresh_token"}
    try:
        response = requests.post(f"{API_URL}/auth/refresh", json=data)
        success = response.status_code == 401
        log_test("POST /auth/refresh - Invalid Token", success)
    except Exception as e:
        log_test("POST /auth/refresh - Invalid Token", False, str(e))


def test_logout(access_token: str):
    """Test logout"""
    print(f"\n{BLUE}=== Testing Logout ==={RESET}")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.post(f"{API_URL}/auth/logout", headers=headers)
        success = response.status_code == 200
        log_test("POST /auth/logout - Success", success)
        if success:
            print(f"   Message: {response.json()['message']}")
    except Exception as e:
        log_test("POST /auth/logout - Success", False, str(e))


def test_use_blacklisted_token(access_token: str):
    """Test using token after logout"""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{API_URL}/auth/me", headers=headers)
        success = response.status_code == 401
        log_test("GET /auth/me - Blacklisted Token", success)
        if success:
            print(f"   Token correctly rejected after logout")
    except Exception as e:
        log_test("GET /auth/me - Blacklisted Token", False, str(e))


def test_docs():
    """Test API documentation"""
    print(f"\n{BLUE}=== Testing Documentation ==={RESET}")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        success = response.status_code == 200 and "swagger" in response.text.lower()
        log_test("GET /docs - Swagger UI", success)
    except Exception as e:
        log_test("GET /docs - Swagger UI", False, str(e))


def main():
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}  JobTracker API - Comprehensive Endpoint Testing{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")

    # Test health
    test_health()

    # Test docs
    test_docs()

    # Test registration
    test_register_success()
    test_register_duplicate()
    test_register_invalid_password()
    test_register_invalid_email()

    # Test login
    tokens = test_login_success()
    test_login_wrong_password()
    test_login_nonexistent_user()

    if tokens:
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Test profile
        test_get_profile(access_token)
        test_get_profile_no_token()
        test_get_profile_invalid_token()

        # Test refresh
        new_tokens = test_refresh_token(refresh_token)
        test_refresh_invalid_token()

        # Test logout
        if new_tokens:
            test_logout(new_tokens["access_token"])
            test_use_blacklisted_token(new_tokens["access_token"])

    # Summary
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}  Test Summary{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")
    print(f"{GREEN}  Passed: {test_results['passed']}{RESET}")
    print(f"{RED}  Failed: {test_results['failed']}{RESET}")
    total = test_results['passed'] + test_results['failed']
    percentage = (test_results['passed'] / total * 100) if total > 0 else 0
    print(f"{BLUE}  Success Rate: {percentage:.1f}%{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}\n")


if __name__ == "__main__":
    main()
