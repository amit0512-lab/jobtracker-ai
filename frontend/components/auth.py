import streamlit as st
from utils.api import login, register, logout


def show_auth_page():
    st.markdown("""
        <div style='text-align:center; padding: 2rem 0 1rem'>
            <h1 style='color:#6C63FF; font-size:2.5rem'>💼 JobTracker AI</h1>
            <p style='color:#888; font-size:1rem'>Track smarter. Apply better.</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    # ── Login ──
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Email aur password dono bharein")
                else:
                    with st.spinner("Logging in..."):
                        res = login(email, password)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["access_token"] = data["access_token"]
                        st.session_state["refresh_token"] = data["refresh_token"]
                        st.session_state["logged_in"] = True
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Login failed"))

    # ── Register ──
    with tab2:
        with st.form("register_form"):
            full_name = st.text_input("Full Name", placeholder="Rahul Sharma")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", help="Minimum 8 characters")
            submitted = st.form_submit_button("Create Account", use_container_width=True)

            if submitted:
                if not all([full_name, email, password]):
                    st.error("Saare fields bharein")
                elif len(password) < 8:
                    st.error("Password kam se kam 8 characters ka hona chahiye")
                else:
                    with st.spinner("Account bana rahe hain..."):
                        res = register(email, full_name, password)
                    if res.status_code == 201:
                        st.success("Account ban gaya! Ab login karo")
                    else:
                        st.error(res.json().get("detail", "Registration failed"))


def show_logout_button():
    with st.sidebar:
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
