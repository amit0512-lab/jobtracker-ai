import requests
import streamlit as st

BASE_URL = "http://localhost:8000/api/v1"


def get_headers():
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


# ─── Auth ─────────────────────────────────────────────────────

def register(email, full_name, password):
    return requests.post(f"{BASE_URL}/auth/register", json={
        "email": email, "full_name": full_name, "password": password
    })

def login(email, password):
    return requests.post(f"{BASE_URL}/auth/login", json={
        "email": email, "password": password
    })

def logout():
    return requests.post(f"{BASE_URL}/auth/logout", headers=get_headers())

def get_profile():
    return requests.get(f"{BASE_URL}/auth/me", headers=get_headers())


# ─── Jobs ─────────────────────────────────────────────────────

def get_jobs(page=1, per_page=10, status=None, search=None):
    params = {"page": page, "per_page": per_page}
    if status and status != "All":
        params["status"] = status.lower()
    if search:
        params["search"] = search
    return requests.get(f"{BASE_URL}/jobs", headers=get_headers(), params=params)

def create_job(data):
    return requests.post(f"{BASE_URL}/jobs", headers=get_headers(), json=data)

def update_job(job_id, data):
    return requests.patch(f"{BASE_URL}/jobs/{job_id}", headers=get_headers(), json=data)

def update_job_status(job_id, new_status):
    return requests.patch(
        f"{BASE_URL}/jobs/{job_id}/status",
        headers=get_headers(),
        params={"new_status": new_status}
    )

def delete_job(job_id):
    return requests.delete(f"{BASE_URL}/jobs/{job_id}", headers=get_headers())


# ─── Resume ───────────────────────────────────────────────────

def upload_resume(file, job_id=None):
    """Upload resume file - file is UploadedFile object from Streamlit"""
    params = {"job_id": job_id} if job_id else {}
    files = {"file": (file.name, file.getvalue(), file.type)}
    return requests.post(
        f"{BASE_URL}/resume",
        headers=get_headers(),
        files=files,
        params=params
    )

def get_resumes():
    return requests.get(f"{BASE_URL}/resume", headers=get_headers())

def analyze_resume(resume_id, job_id):
    return requests.get(
        f"{BASE_URL}/resume/{resume_id}/analyze",
        headers=get_headers(),
        params={"job_id": job_id}
    )

def delete_resume(resume_id):
    return requests.delete(f"{BASE_URL}/resume/{resume_id}", headers=get_headers())


# ─── Analytics ────────────────────────────────────────────────

def get_dashboard():
    return requests.get(f"{BASE_URL}/analytics/dashboard", headers=get_headers())

def get_timeline():
    return requests.get(f"{BASE_URL}/analytics/timeline", headers=get_headers())