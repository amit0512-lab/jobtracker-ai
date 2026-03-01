import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Colors
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


def setup_user():
    """Create user and login to get token"""
    print(f"\n{BLUE}=== Setup: Creating User & Login ==={RESET}")
    
    # Register
    register_data = {
        "email": "jobuser@example.com",
        "full_name": "Job User",
        "password": "password123"
    }
    requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    # Login
    login_data = {
        "email": "jobuser@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"   Token obtained: {token[:30]}...")
        return token
    return None


def test_create_job(token):
    """Test creating a new job"""
    print(f"\n{BLUE}=== Testing Create Job ==={RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Senior Python Developer",
        "company": "Tech Corp",
        "location": "Remote",
        "job_url": "https://example.com/job/123",
        "description": "Looking for experienced Python developer with FastAPI knowledge",
        "priority": "high",
        "notes": "Great opportunity",
        "salary_min": "100000",
        "salary_max": "150000"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/jobs", json=data, headers=headers)
        success = response.status_code == 201
        log_test("POST /jobs - Create Job", success)
        if success:
            job = response.json()
            print(f"   Job ID: {job['id']}")
            print(f"   Title: {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Status: {job['status']}")
            return job
    except Exception as e:
        log_test("POST /jobs - Create Job", False, str(e))
    return None


def test_create_multiple_jobs(token):
    """Create multiple jobs for testing list/filter"""
    print(f"\n{BLUE}=== Creating Multiple Jobs ==={RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    
    jobs_data = [
        {"title": "Frontend Developer", "company": "StartupX", "priority": "medium"},
        {"title": "Backend Engineer", "company": "BigCorp", "priority": "low"},
        {"title": "Full Stack Dev", "company": "MidSize Inc", "priority": "high"},
    ]
    
    created = []
    for job_data in jobs_data:
        response = requests.post(f"{BASE_URL}/jobs", json=job_data, headers=headers)
        if response.status_code == 201:
            created.append(response.json())
    
    print(f"   Created {len(created)} additional jobs")
    return created


def test_get_all_jobs(token):
    """Test getting all jobs"""
    print(f"\n{BLUE}=== Testing Get All Jobs ==={RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/jobs", headers=headers)
        success = response.status_code == 200
        log_test("GET /jobs - List All", success)
        if success:
            data = response.json()
            print(f"   Total jobs: {data['total']}")
            print(f"   Page: {data['page']}")
            print(f"   Per page: {data['per_page']}")
            print(f"   Jobs returned: {len(data['jobs'])}")
            return data
    except Exception as e:
        log_test("GET /jobs - List All", False, str(e))
    return None


def test_get_jobs_pagination(token):
    """Test pagination"""
    print(f"\n{BLUE}=== Testing Pagination ==={RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/jobs?page=1&per_page=2", headers=headers)
        success = response.status_code == 200 and len(response.json()['jobs']) <= 2
        log_test("GET /jobs - Pagination", success)
        if success:
            print(f"   Returned {len(response.json()['jobs'])} jobs (max 2)")
    except Exception as e:
        log_test("GET /jobs - Pagination", False, str(e))


def test_get_jobs_filter_status(token):
    """Test filtering by status"""
    print(f"\n{BLUE}=== Testing Filter by Status ==={RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/jobs?status=saved", headers=headers)
        success = response.status_code == 200
        log_test("GET /jobs - Filter by Status", success)
        if success:
            jobs = response.json()['jobs']
            all_saved = all(job['status'] == 'saved' for job in jobs)
            print(f"   All jobs have status 'saved': {all_saved}")
    except Exception as e:
        log_test("GET /jobs - Filter by Status", False, str(e))


def test_get_jobs_search(token):
    """Test search functionality"""
    print(f"\n{BLUE}=== Testing Search ==={RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/jobs?search=Python", headers=headers)
        success = response.status_code == 200
        log_test("GET /jobs - Search", success)
        if success:
            jobs = response.json()['jobs']
            print(f"   Found {len(jobs)} jobs matching 'Python'")
    except Exception as e:
        log_test("GET /jobs - Search", False, str(e))


def test_get_single_job(token, job_id):
    """Test getting a single job"""
    print(f"\n{BLUE}=== Testing Get Single Job ==={RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/jobs/{job_id}", headers=headers)
        success = response.status_code == 200
        log_test("GET /jobs/{id} - Get Single Job", success)
        if success:
            job = response.json()
            print(f"   Job: {job['title']} at {job['company']}")
    except Exception as e:
        log_test("GET /jobs/{id} - Get Single Job", False, str(e))


def test_update_job(token, job_id):
    """Test updating a job"""
    print(f"\n{BLUE}=== Testing Update Job ==={RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "notes": "Updated notes - very interested!",
        "salary_min": "120000"
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/jobs/{job_id}", json=data, headers=headers)
        success = response.status_code == 200
        log_test("PATCH /jobs/{id} - Update Job", success)
        if success:
            job = response.json()
            print(f"   Updated notes: {job['notes']}")
            print(f"   Updated salary_min: {job['salary_min']}")
    except Exception as e:
        log_test("PATCH /jobs/{id} - Update Job", False, str(e))


def test_update_status(token, job_id):
    """Test updating job status"""
    print(f"\n{BLUE}=== Testing Update Status ==={RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.patch(
            f"{BASE_URL}/jobs/{job_id}/status?new_status=applied",
            headers=headers
        )
        success = response.status_code == 200
        log_test("PATCH /jobs/{id}/status - Update Status", success)
        if success:
            job = response.json()
            print(f"   New status: {job['status']}")
            print(f"   Applied at: {job['applied_at']}")
    except Exception as e:
        log_test("PATCH /jobs/{id}/status - Update Status", False, str(e))


def test_delete_job(token, job_id):
    """Test deleting a job"""
    print(f"\n{BLUE}=== Testing Delete Job ==={RESET}")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/jobs/{job_id}", headers=headers)
        success = response.status_code == 200
        log_test("DELETE /jobs/{id} - Delete Job", success)
        if success:
            print(f"   Message: {response.json()['message']}")
    except Exception as e:
        log_test("DELETE /jobs/{id} - Delete Job", False, str(e))


def test_get_deleted_job(token, job_id):
    """Test getting a deleted job (should fail)"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/jobs/{job_id}", headers=headers)
        success = response.status_code == 404
        log_test("GET /jobs/{id} - Deleted Job (404)", success)
    except Exception as e:
        log_test("GET /jobs/{id} - Deleted Job (404)", False, str(e))


def test_unauthorized_access():
    """Test accessing jobs without token"""
    print(f"\n{BLUE}=== Testing Unauthorized Access ==={RESET}")
    
    try:
        response = requests.get(f"{BASE_URL}/jobs")
        success = response.status_code == 403
        log_test("GET /jobs - No Token (403)", success)
    except Exception as e:
        log_test("GET /jobs - No Token (403)", False, str(e))


def main():
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}  JobTracker - Jobs Endpoints Testing{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")

    # Setup
    token = setup_user()
    if not token:
        print(f"{RED}Failed to get auth token. Exiting.{RESET}")
        return

    # Test unauthorized access
    test_unauthorized_access()

    # Create jobs
    first_job = test_create_job(token)
    additional_jobs = test_create_multiple_jobs(token)

    if first_job:
        job_id = first_job['id']

        # List and filter
        test_get_all_jobs(token)
        test_get_jobs_pagination(token)
        test_get_jobs_filter_status(token)
        test_get_jobs_search(token)

        # Single job operations
        test_get_single_job(token, job_id)
        test_update_job(token, job_id)
        test_update_status(token, job_id)

        # Delete
        test_delete_job(token, job_id)
        test_get_deleted_job(token, job_id)

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
