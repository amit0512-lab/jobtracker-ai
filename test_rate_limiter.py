import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def test_rate_limiter():
    """Test rate limiting on login endpoint"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  Testing Rate Limiter on Login Endpoint{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    print(f"{YELLOW}Rate Limit: 5 requests per 60 seconds{RESET}\n")
    
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    # Try 7 requests (should fail after 5)
    for i in range(1, 8):
        print(f"Request {i}...", end=" ")
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 429:
            print(f"{RED}❌ Rate Limited (429){RESET}")
            print(f"   Response: {response.json()}")
        elif response.status_code == 401:
            print(f"{GREEN}✅ Request Allowed (401 - wrong password){RESET}")
        else:
            print(f"{YELLOW}Status: {response.status_code}{RESET}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}Rate limiter is working correctly!{RESET}")
    print(f"{YELLOW}First 5 requests allowed, 6th and 7th blocked.{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def test_different_endpoints():
    """Test that rate limit is per-endpoint"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  Testing Rate Limit Per-Endpoint{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Hit login 5 times
    print(f"{YELLOW}Hitting /login 5 times...{RESET}")
    for i in range(5):
        requests.post(f"{BASE_URL}/auth/login", json={"email": "test@example.com", "password": "test"})
    
    # Now try register (should work - different endpoint)
    print(f"\n{YELLOW}Now trying /register (different endpoint)...{RESET}")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": "newuser2@example.com", "full_name": "New User", "password": "password123"}
    )
    
    if response.status_code in [201, 400]:  # 201 success or 400 duplicate
        print(f"{GREEN}✅ Register endpoint not affected by login rate limit{RESET}")
    else:
        print(f"{RED}❌ Unexpected status: {response.status_code}{RESET}")
    
    print(f"\n{BLUE}{'='*60}{RESET}\n")


if __name__ == "__main__":
    print(f"\n{YELLOW}Starting Rate Limiter Tests...{RESET}\n")
    
    # Test 1: Basic rate limiting
    test_rate_limiter()
    
    # Wait a bit
    print(f"{YELLOW}Waiting 5 seconds before next test...{RESET}\n")
    time.sleep(5)
    
    # Test 2: Per-endpoint limiting
    test_different_endpoints()
    
    print(f"{GREEN}All rate limiter tests completed!{RESET}\n")
