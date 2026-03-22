from pathlib import Path
import streamlit as st

from services.auth_service import signup as api_signup

VIEWS_DIR = Path(__file__).parent

st.title("Create your account")
st.caption("Energy-aware scheduling for students who can't afford burnout")

with st.form("signup_form", clear_on_submit=False):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")
    submitted = st.form_submit_button("Create account", use_container_width=True)

if submitted:
    if not username.strip() or not password:
        st.warning("Please enter a username and password.")
        st.stop()

    if password != confirm_password:
        st.error("Passwords do not match.")
        st.stop()

    if len(password) < 6:
        st.warning("Password must be at least 6 characters.")
        st.stop()

    with st.spinner("Creating your account..."):
        try:
            token, user = api_signup(username.strip(), password)
        except Exception as e:
            st.error(f"Sign up failed: {e}")
        else:
            st.session_state["token"] = token
            st.session_state["user"] = user
            st.success("Account created! Redirecting...")
            st.rerun()

st.divider()
st.markdown("Already have an account?")
if st.button("Sign in", use_container_width=True):
    st.switch_page(VIEWS_DIR / "login.py")
