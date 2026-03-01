import streamlit as st
from utils.api import get_jobs, create_job, update_job_status, delete_job, update_job
from components.auth import show_logout_button

# Auth guard
if not st.session_state.get("logged_in"):
    st.warning("Pehle login karo"); st.stop()

show_logout_button()

st.markdown("## 💼 Job Applications")

# ─── Add Job Form ─────────────────────────────────────────────
with st.expander("➕ Naya Job Add Karo", expanded=False):
    with st.form("add_job_form"):
        c1, c2 = st.columns(2)
        with c1:
            title    = st.text_input("Job Title*", placeholder="Backend Developer")
            company  = st.text_input("Company*",   placeholder="Google")
            location = st.text_input("Location",   placeholder="Bangalore / Remote")
        with c2:
            job_url  = st.text_input("Job URL",    placeholder="https://...")
            priority = st.selectbox("Priority", ["medium", "high", "low"])
            salary   = st.text_input("Salary Range", placeholder="15-20 LPA")

        description = st.text_area(
            "Job Description (JD)*",
            placeholder="Paste full JD here — NLP matching ke liye zaroori hai",
            height=150
        )
        notes = st.text_area("Personal Notes", placeholder="Referral hai, HR ka naam...", height=80)

        if st.form_submit_button("Add Job ✅", use_container_width=True):
            if not title or not company:
                st.error("Title aur Company zaroori hain")
            else:
                sal_parts = salary.split("-") if salary else []
                res = create_job({
                    "title": title, "company": company,
                    "location": location, "job_url": job_url,
                    "description": description, "priority": priority,
                    "notes": notes,
                    "salary_min": sal_parts[0].strip() if len(sal_parts) > 0 else None,
                    "salary_max": sal_parts[1].strip() if len(sal_parts) > 1 else None,
                })
                if res.status_code == 201:
                    st.success("Job add ho gayi! ✅")
                    st.rerun()
                else:
                    st.error("Job add nahi hui")

st.divider()

# ─── Filters ──────────────────────────────────────────────────
fc1, fc2, fc3 = st.columns([2, 1, 1])
with fc1:
    search = st.text_input("🔍 Search", placeholder="Company ya title...")
with fc2:
    status_filter = st.selectbox(
        "Status", ["All", "Saved", "Applied", "Interview", "Offer", "Rejected"]
    )
with fc3:
    per_page = st.selectbox("Per Page", [5, 10, 20], index=1)

# ─── Jobs List ────────────────────────────────────────────────
res = get_jobs(
    page=st.session_state.get("jobs_page", 1),
    per_page=per_page,
    status=status_filter,
    search=search
)

if res.status_code != 200:
    st.error("Jobs load nahi hui"); st.stop()

data  = res.json()
jobs  = data["jobs"]
total = data["total"]

# Status color mapping
STATUS_COLORS = {
    "saved":     "🔵", "applied":   "🟡",
    "interview": "🟠", "offer":     "🟢", "rejected":  "🔴"
}
PRIORITY_COLORS = {"high": "🔴", "medium": "🟡", "low": "🟢"}

if not jobs:
    st.info("Koi job nahi mili. Upar se add karo!")
else:
    st.caption(f"Total: **{total}** jobs")

    for job in jobs:
        status_icon   = STATUS_COLORS.get(job["status"], "⚪")
        priority_icon = PRIORITY_COLORS.get(job["priority"], "⚪")

        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 2, 2])

            with col1:
                st.markdown(f"### {job['title']}")
                st.markdown(
                    f"🏢 **{job['company']}**"
                    + (f"  •  📍 {job['location']}" if job.get('location') else "")
                    + (f"  •  💰 {job['salary_min']}-{job['salary_max']}" if job.get('salary_min') else "")
                )
                if job.get("notes"):
                    st.caption(f"📝 {job['notes']}")

            with col2:
                st.markdown(f"**Status:** {status_icon} {job['status'].title()}")
                st.markdown(f"**Priority:** {priority_icon} {job['priority'].title()}")
                if job.get("applied_at"):
                    st.caption(f"Applied: {job['applied_at'][:10]}")

            with col3:
                # Status update
                new_status = st.selectbox(
                    "Update Status",
                    ["saved", "applied", "interview", "offer", "rejected"],
                    index=["saved","applied","interview","offer","rejected"].index(job["status"]),
                    key=f"status_{job['id']}"
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Update", key=f"upd_{job['id']}", use_container_width=True):
                        update_job_status(job["id"], new_status)
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_{job['id']}", use_container_width=True):
                        delete_job(job["id"])
                        st.rerun()

# ─── Pagination ───────────────────────────────────────────────
if total > per_page:
    total_pages = (total + per_page - 1) // per_page
    current_page = st.session_state.get("jobs_page", 1)

    p1, p2, p3 = st.columns([1, 2, 1])
    with p1:
        if st.button("⬅️ Prev") and current_page > 1:
            st.session_state["jobs_page"] = current_page - 1
            st.rerun()
    with p2:
        st.markdown(
            f"<p style='text-align:center'>Page {current_page} / {total_pages}</p>",
            unsafe_allow_html=True
        )
    with p3:
        if st.button("Next ➡️") and current_page < total_pages:
            st.session_state["jobs_page"] = current_page + 1
            st.rerun()