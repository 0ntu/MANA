from pathlib import Path
import streamlit as st

from services.auth_service import login as api_login

VIEWS_DIR = Path(__file__).parent

st.title("Sign in")
st.caption("Energy-aware scheduling for students who can't afford burnout")

with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Sign in", use_container_width=True)

if submitted:
    if not username.strip() or not password:
        st.warning("Please enter your username and password.")
        st.stop()

    with st.spinner("Signing in..."):
        try:
            token, user = api_login(username.strip(), password)
        except Exception as e:
            st.error(f"Sign in failed: {e}")
        else:
            st.session_state["token"] = token
            st.session_state["user"] = user
            st.success("Signed in! Redirecting...")
            st.rerun()

st.divider()
st.markdown("Don't have an account?")
if st.button("Create account", use_container_width=True):
    st.switch_page(VIEWS_DIR / "signup.py")
