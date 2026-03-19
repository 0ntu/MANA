import streamlit as st
st.set_page_config(page_title="UF MANA", page_icon=":robot_face:", layout="wide")

st.title("UF MANA")
st.caption("Energy-aware scheduling for students who can't afford burnout")

token = st.session_state.get("token")
user = st.session_state.get("user")

if token:
    st.sidebar.success(f"Signed in as {user.get('username', user.get('name', 'User'))}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
else:
    st.sidebar.success("Welcome to UF MANA! Please sign up or log in from the pages menu.")