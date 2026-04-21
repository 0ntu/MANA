from pathlib import Path
import streamlit as st

st.set_page_config(page_title="UF MANA", page_icon=":diamond_shape_with_a_dot_inside:", layout="wide")

APP_DIR = Path(__file__).parent

#font smoothing
st.html("""
<style>
body {
    -webkit-font-smoothing: antialiased;
}
</style>
""")

# public schedule route, no auth required
if st.query_params.get("page") == "public_schedule":
    exec(open(APP_DIR / "views" / "public_schedule.py").read())
    st.stop()


def home_page():
    st.title("UF MANA")
    st.caption("Energy-aware scheduling for students who can't afford burnout")

    token = st.session_state.get("token")
    user = st.session_state.get("user")

    if token and user:
        username = user.get("username", "User")
        st.write(f"Welcome back, **{username}**! Head to the Dashboard to see your energy plan for today.")
    else:
        st.write("Track your energy levels and plan your day around what you can actually handle.")
        st.write("Sign in or create an account to get started.")


def logout():
    st.session_state.clear()
    st.rerun()


token = st.session_state.get("token")
user = st.session_state.get("user")

if token and user:
    # loggedin sidebar
    pages = {
        "": [
            st.Page(home_page, title="Home", icon=":material/home:"),
            st.Page(APP_DIR / "views" / "dashboard.py", title="Dashboard", icon=":material/dashboard:"),
        ],
        "Tasks": [
            st.Page(APP_DIR / "views" / "schedule_today.py", title="Today's Schedule", icon=":material/today:"),
            st.Page(APP_DIR / "views" / "calendar.py", title="Monthly Overview", icon=":material/calendar_month:"),
            st.Page(APP_DIR / "views" / "add_event.py", title="Add Task", icon=":material/add_task:"),
        ],
        "Energy": [
            st.Page(APP_DIR / "views" / "log_mana.py", title="Log Mana", icon=":material/battery_charging_full:"),
            st.Page(APP_DIR / "views" / "view_energy_graph.py", title="Energy History", icon=":material/insights:"),
        ],
        "Settings": [
            st.Page(APP_DIR / "views" / "share_settings.py", title="Share Schedule", icon=":material/share:"),
        ],
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
