import streamlit as st

st.set_page_config(page_title="UF MANA", page_icon=":robot_face:", layout="wide")

st.title("UF MANA")
st.caption("Energy-aware scheduling for students who can't afford burnout")

token = st.session_state.get("token")
user = st.session_state.get("user")

if token and user:
    username = user.get("username", "User")
    st.sidebar.success(f"Signed in as **{username}**")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.write(f"Welcome back, **{username}**! Head to the Dashboard to see your energy plan for today.")
    if st.button("Go to Dashboard", use_container_width=False):
        st.switch_page("pages/dashboard.py")
else:
    st.sidebar.info("Please sign in or create an account.")

    col1, col2 = st.columns(2, gap="small")
    with col1:
        if st.button("Sign in", use_container_width=True):
            st.switch_page("pages/login.py")
    with col2:
        if st.button("Create account", use_container_width=True):
            st.switch_page("pages/signup.py")
