"""
Test Cover Letter Generation Feature
Run: python test_cover_letter.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Test credentials (use your actual test user)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def test_cover_letter_flow():
    """Test complete cover letter generation flow"""
    
    print("🧪 Testing Cover Letter Feature\n")
    
    # 1. Login
    print("1️⃣ Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed. Please create a test user first.")
        print(f"   Register at: {BASE_URL}/auth/register")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful\n")
    
    # 2. Get jobs
    print("2️⃣ Fetching jobs...")
    jobs_response = requests.get(f"{BASE_URL}/jobs", headers=headers)
    jobs = jobs_response.json()
    
    if not jobs or len(jobs) == 0:
        print("❌ No jobs found. Please add a job with description first.")
        return
    
    job = jobs[0]
    print(f"✅ Found job: {job['title']} @ {job['company']}\n")
    
    # 3. Get resumes (optional)
    print("3️⃣ Fetching resumes...")
    resumes_response = requests.get(f"{BASE_URL}/resume", headers=headers)
    resumes = resumes_response.json()
    resume_id = resumes[0]["id"] if resumes and len(resumes) > 0 else None
    
    if resume_id:
        print(f"✅ Found resume: {resumes[0]['filename']}\n")
    else:
        print("⚠️  No resume found, will use generic template\n")
    
    # 4. Generate cover letter
    print("4️⃣ Generating cover letter...")
    print("   (This may take 5-10 seconds with OpenAI API)")
    
    generate_data = {
        "job_id": job["id"],
        "resume_id": resume_id,
        "tone": "professional"
    }
    
    generate_response = requests.post(
        f"{BASE_URL}/cover-letter/generate",
        headers=headers,
        json=generate_data
    )
    
    if generate_response.status_code != 201:
        print(f"❌ Generation failed: {generate_response.text}")
        return
    
    cover_letter = generate_response.json()
    print("✅ Cover letter generated successfully!\n")
    
    # 5. Display results
    print("=" * 60)
    print("📄 GENERATED COVER LETTER")
    print("=" * 60)
    print(f"ID: {cover_letter['id']}")
    print(f"Tone: {cover_letter['tone']}")
    print(f"Word Count: {cover_letter['word_count']}")
    print(f"\nContent:\n")
    print(cover_letter['content'])
    print("\n" + "=" * 60)
    
    # 6. Test retrieval
    print("\n5️⃣ Testing retrieval...")
    get_response = requests.get(
        f"{BASE_URL}/cover-letter/{cover_letter['id']}",
        headers=headers
    )
    
    if get_response.status_code == 200:
        print("✅ Retrieval successful\n")
    else:
        print("❌ Retrieval failed\n")
    
    # 7. Test update
    print("6️⃣ Testing update...")
    update_data = {
        "content": cover_letter['content'] + "\n\nP.S. This is a test update."
    }
    
    update_response = requests.patch(
        f"{BASE_URL}/cover-letter/{cover_letter['id']}",
        headers=headers,
        json=update_data
    )
    
    if update_response.status_code == 200:
        print("✅ Update successful\n")
    else:
        print("❌ Update failed\n")
    
    # 8. Test list
    print("7️⃣ Testing list...")
    list_response = requests.get(f"{BASE_URL}/cover-letter", headers=headers)
    
    if list_response.status_code == 200:
        cover_letters = list_response.json()
        print(f"✅ Found {len(cover_letters)} cover letter(s)\n")
    else:
        print("❌ List failed\n")
    
    # 9. Test delete
    print("8️⃣ Testing delete...")
    delete_response = requests.delete(
        f"{BASE_URL}/cover-letter/{cover_letter['id']}",
        headers=headers
    )
    
    if delete_response.status_code == 200:
        print("✅ Delete successful\n")
    else:
        print("❌ Delete failed\n")
    
    print("=" * 60)
    print("🎉 ALL TESTS COMPLETED!")
    print("=" * 60)
    print("\n💡 Tips:")
    print("   - Add OPENAI_API_KEY to .env for AI generation")
    print("   - Without API key, template-based generation is used")
    print("   - Try different tones: professional, enthusiastic, creative, formal")
    print("   - Frontend available at: http://localhost:3000")


if __name__ == "__main__":
    try:
        test_cover_letter_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
