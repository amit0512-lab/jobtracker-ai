import streamlit as st

# Check if logged in
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Pehle login karo!")
    st.info("👈 Sidebar se 'app' (Home) page pe jao aur login karo")
    st.stop()

# Import after auth check
from utils.api import upload_resume, get_resumes, get_jobs, analyze_resume, delete_resume
from components.auth import show_logout_button

show_logout_button()

st.markdown("## 📄 Resume Manager")
st.write("Upload your resume and analyze it against job descriptions")

# ─── Upload Resume Section ────────────────────────────────────
with st.expander("📤 Upload New Resume", expanded=True):
    uploaded_file = st.file_uploader(
        "Choose a file (PDF/DOCX)",
        type=["pdf", "docx", "doc"],
        help="Upload your latest resume for NLP parsing"
    )
    
    # Get jobs for optional linking
    try:
        jobs_res = get_jobs(page=1, per_page=50)
        job_options = {"None - General Resume": None}
        
        if jobs_res.status_code == 200:
            jobs_data = jobs_res.json()
            for job in jobs_data["jobs"]:
                job_options[f"{job['title']} @ {job['company']}"] = job["id"]
    except Exception as e:
        st.error(f"Could not load jobs: {e}")
        job_options = {"None - General Resume": None}
    
    selected_job = st.selectbox(
        "Link to a specific job? (Optional)",
        options=list(job_options.keys())
    )
    
    if st.button("📤 Upload Resume", use_container_width=True, type="primary"):
        if not uploaded_file:
            st.error("Please select a file first")
        else:
            with st.spinner("Uploading and parsing resume..."):
                try:
                    job_id = job_options[selected_job]
                    res = upload_resume(uploaded_file, job_id)
                    
                    if res.status_code == 201:
                        st.success("✅ Resume uploaded successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        error_msg = res.json().get('detail', 'Unknown error')
                        st.error(f"Upload failed: {error_msg}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.divider()

# ─── Resumes List ─────────────────────────────────────────────
st.markdown("### � Your Resumes")

try:
    res = get_resumes()
    
    if res.status_code != 200:
        st.error(f"Could not load resumes: {res.status_code}")
        st.stop()
    
    resumes = res.json()
    
    if not resumes:
        st.info("📭 No resumes uploaded yet. Upload one above!")
    else:
        st.caption(f"Total: **{len(resumes)}** resume(s)")
        
        for idx, resume in enumerate(resumes):
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.markdown(f"### 📄 {resume['filename']}")
                    st.caption(f"📅 Uploaded: {resume['created_at'][:10]}")
                    if resume.get('file_size'):
                        st.caption(f"💾 Size: {resume['file_size']}")
                
                with col2:
                    # Match score
                    score = resume.get('match_score', 0)
                    if score > 0:
                        color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                        st.metric("Match Score", f"{score}%")
                        st.caption(f"{color} {'Excellent' if score >= 70 else 'Good' if score >= 50 else 'Needs Work'}")
                    else:
                        st.caption("⚪ No match score yet")
                    
                    # Skills count
                    skills_count = len(resume.get('extracted_skills', []))
                    st.caption(f"🎯 {skills_count} skills extracted")
                
                with col3:
                    # Analyze button
                    if st.button("� Analyze", key=f"analyze_{idx}", use_container_width=True):
                        st.session_state[f"show_analyze_{resume['id']}"] = True
                        st.rerun()
                    
                    # Delete button
                    if st.button("🗑️ Delete", key=f"del_{idx}", use_container_width=True):
                        with st.spinner("Deleting..."):
                            try:
                                del_res = delete_resume(resume['id'])
                                if del_res.status_code == 200:
                                    st.success("Deleted!")
                                    st.rerun()
                                else:
                                    st.error("Delete failed")
                            except Exception as e:
                                st.error(f"Error: {e}")
                
                # Show extracted info
                with st.expander("📊 View Extracted Information"):
                    info_col1, info_col2 = st.columns(2)
                    
                    with info_col1:
                        st.markdown("**🎯 Skills:**")
                        skills = resume.get('extracted_skills', [])
                        if skills:
                            st.write(", ".join(skills[:15]))
                        else:
                            st.caption("No skills extracted")
                    
                    with info_col2:
                        st.markdown("**🔑 Keywords:**")
                        keywords = resume.get('keywords', [])
                        if keywords:
                            st.write(", ".join(keywords[:15]))
                        else:
                            st.caption("No keywords extracted")
                    
                    # Experience
                    experience = resume.get('extracted_experience', [])
                    if experience:
                        st.markdown("**💼 Experience:**")
                        for exp in experience[:3]:
                            st.caption(f"• {exp.get('raw', 'N/A')[:100]}...")
                    
                    # Education
                    education = resume.get('extracted_education', [])
                    if education:
                        st.markdown("**🎓 Education:**")
                        for edu in education[:3]:
                            degree = edu.get('degree', 'N/A')
                            context = edu.get('context', '')[:80]
                            st.caption(f"• {degree} - {context}...")
                
                # Analyze Modal
                if st.session_state.get(f"show_analyze_{resume['id']}", False):
                    st.markdown("---")
                    st.markdown("### 🔍 Analyze Resume Against Job")
                    
                    # Job selection for analysis
                    job_list = [k for k in job_options.keys() if k != "None - General Resume"]
                    
                    if not job_list:
                        st.warning("No jobs available. Add a job first!")
                    else:
                        analyze_job = st.selectbox(
                            "Select job to match against:",
                            options=job_list,
                            key=f"job_select_{idx}"
                        )
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("🚀 Analyze Now", key=f"analyze_btn_{idx}", use_container_width=True, type="primary"):
                                job_id = job_options[analyze_job]
                                with st.spinner("Analyzing... NLP magic happening 🪄"):
                                    try:
                                        analysis_res = analyze_resume(resume['id'], job_id)
                                        
                                        if analysis_res.status_code == 200:
                                            analysis = analysis_res.json()
                                            
                                            st.success("✅ Analysis Complete!")
                                            
                                            # Match Score
                                            score = analysis['match_score']
                                            st.metric("🎯 Match Score", f"{score}%")
                                            st.progress(score / 100)
                                            
                                            # Matched Keywords
                                            st.markdown("**✅ Matched Keywords:**")
                                            matched = analysis.get('matched_keywords', [])
                                            if matched:
                                                st.success(", ".join(matched[:20]))
                                            else:
                                                st.caption("None")
                                            
                                            # Missing Keywords
                                            st.markdown("**❌ Missing Keywords:**")
                                            missing = analysis.get('missing_keywords', [])
                                            if missing:
                                                st.error(", ".join(missing[:15]))
                                            else:
                                                st.caption("None")
                                            
                                            # Suggestions
                                            st.markdown("**💡 Suggestions:**")
                                            suggestions = analysis.get('suggestions', [])
                                            for suggestion in suggestions:
                                                st.info(suggestion)
                                        else:
                                            st.error(f"Analysis failed: {analysis_res.json().get('detail', 'Unknown error')}")
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                        
                        with col_b:
                            if st.button("❌ Cancel", key=f"cancel_{idx}", use_container_width=True):
                                st.session_state[f"show_analyze_{resume['id']}"] = False
                                st.rerun()

except Exception as e:
    st.error(f"Error loading resumes: {str(e)}")
    st.info("Make sure the backend API is running on http://localhost:8000")

# ─── Tips Section ─────────────────────────────────────────────
st.divider()
st.markdown("### 💡 Tips for Better Results")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
        **📄 Resume Format**
        - Use PDF or DOCX format
        - Keep formatting clean
        - Include relevant keywords
    """)

with col2:
    st.info("""
        **🎯 Better Matching**
        - Mention skills from JD
        - Add quantifiable achievements
        - Use industry keywords
    """)

with col3:
    st.info("""
        **🔍 Analysis**
        - Analyze for each job
        - Note missing keywords
        - Update resume accordingly
    """)
