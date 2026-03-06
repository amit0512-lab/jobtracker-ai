"""
Direct test of cover letter generation endpoint
"""
import requests
import json

# Register a new test user
print("🔄 Registering test user...")
register_response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "email": "testcl@example.com",
        "password": "test123",
        "full_name": "Test CL User"
    }
)

if register_response.status_code not in [200, 201]:
    print(f"⚠️  Registration response: {register_response.status_code}")
    # User might already exist, try to login
else:
    print("✅ Registration successful")

# Login
print("\n🔄 Logging in...")
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "email": "testcl@example.com",
        "password": "test123"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Login successful")

# Create a test job first
print("\n🔄 Creating test job...")
job_response = requests.post(
    "http://localhost:8000/api/v1/jobs",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "title": "Python Developer",
        "company": "Test Company",
        "location": "Remote",
        "description": "We are looking for a Python developer with FastAPI experience. Must know Docker and PostgreSQL.",
        "status": "applied"
    }
)

if job_response.status_code not in [200, 201]:
    print(f"❌ Failed to create job: {job_response.status_code}")
    print(job_response.text)
    # Try to get existing jobs
    jobs_response = requests.get(
        "http://localhost:8000/api/v1/jobs",
        headers={"Authorization": f"Bearer {token}"}
    )
    jobs = jobs_response.json()
    if isinstance(jobs, dict) and "jobs" in jobs:
        jobs = jobs["jobs"]
    if not jobs:
        print("❌ No jobs found")
        exit(1)
    job_id = jobs[0]["id"]
else:
    job_id = job_response.json()["id"]
    print(f"✅ Job created: {job_id}")

# Try to generate cover letter
print("\n🔄 Attempting to generate cover letter...")
print("This may take 30-60 seconds...")
try:
    cover_letter_response = requests.post(
        "http://localhost:8000/api/v1/cover-letter/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "job_id": job_id,
            "resume_id": None,
            "tone": "professional"
        },
        timeout=120
    )
    
    print(f"\n📊 Response Status: {cover_letter_response.status_code}")
    print(f"📊 Response Headers:")
    for key, value in cover_letter_response.headers.items():
        print(f"  {key}: {value}")
    
    print(f"\n📄 Response Body:")
    try:
        print(json.dumps(cover_letter_response.json(), indent=2))
    except:
        print(cover_letter_response.text)
    
    if cover_letter_response.status_code == 201:
        print("\n✅ Cover letter generated successfully!")
    else:
        print(f"\n❌ Failed with status {cover_letter_response.status_code}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out after 120 seconds")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

