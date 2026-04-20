from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Energy Scheduler", page_icon=":zap:", layout="wide")

APP_DIR = Path(__file__).parent

# Custom CSS for a modern, structured layout
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f9f9f9;
        color: #333;
        margin: 0;
        padding: 0;
    }

    if user.get("role") == "admin":
        pages["Admin"] = [
            st.Page(APP_DIR / "views" / "admin_panel.py", title="Admin Panel", icon=":material/admin_panel_settings:"),
        ]

    nav = st.navigation(pages)

    with st.sidebar:
        st.divider()
        st.success(f"Signed in as **{user.get('username', 'User')}**")
        if st.button("Logout", use_container_width=True):
            logout()
else:
    # logged out sidebar
    pages = [
        st.Page(home_page, title="Home", icon=":material/home:"),
        st.Page(APP_DIR / "views" / "login.py", title="Sign In", icon=":material/login:"),
        st.Page(APP_DIR / "views" / "signup.py", title="Create Account", icon=":material/person_add:"),
    ]

    nav = st.navigation(pages)

nav.run()
