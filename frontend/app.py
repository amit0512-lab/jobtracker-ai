import streamlit as st
from components.auth import show_auth_page, show_logout_button
from utils.api import get_profile

st.set_page_config(
    page_title="JobTracker AI",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Session State Init ───────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ─── Auth Guard ───────────────────────────────────────────────
if not st.session_state["logged_in"]:
    show_auth_page()
    st.stop()

# ─── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    # User profile
    res = get_profile()
    if res.status_code == 200:
        user = res.json()
        st.markdown(f"""
            <div style='
                background: #1A1D27;
                border-radius: 12px;
                padding: 1rem;
                margin-bottom: 1rem;
                border-left: 3px solid #6C63FF;
            '>
                <p style='margin:0; color:#888; font-size:0.75rem'>Logged in as</p>
                <p style='margin:0; font-weight:bold; font-size:1rem'>
                    {user['full_name']}
                </p>
                <p style='margin:0; color:#888; font-size:0.8rem'>{user['email']}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("## 📌 Navigation")
    st.page_link("app.py",               label="🏠 Home",      icon="🏠")
    st.page_link("pages/1_Jobs.py",      label="💼 Jobs",      icon="💼")
    st.page_link("pages/2_Resume.py",    label="📄 Resume",    icon="📄")
    st.page_link("pages/3_Analytics.py", label="📊 Analytics", icon="📊")

    show_logout_button()

# ─── Home Page ────────────────────────────────────────────────
st.markdown("""
    <h1 style='color:#6C63FF'>💼 JobTracker AI</h1>
    <p style='color:#888; font-size:1.1rem'>
        Apne job applications track karo — AI-powered resume analysis ke saath
    </p>
""", unsafe_allow_html=True)

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.info("💼 **Jobs**\n\nNaye jobs add karo, status track karo")
with col2:
    st.info("📄 **Resume**\n\nResume upload karo, JD se match karo")
with col3:
    st.info("📊 **Analytics**\n\nApplications ka poora breakdown dekho")