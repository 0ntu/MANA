import streamlit as st

from services.auth_service import signup as api_signup


st.title("Sign Up")

with st.form("signup_form", clear_on_submit=False):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Create account")

if submitted:
    if not username.strip() or not password:
        st.warning("Please enter a username and password.")
        st.stop()

    try:
        token, user = api_signup(username.strip(), password)
    except Exception as e:
        st.error(f"Signup failed: {e}")
    else:
        st.session_state["token"] = token
        st.session_state["user"] = user
        st.success("Account created. You're now signed in.")

