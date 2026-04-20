import streamlit as st

from services.share_service import get_public_schedule


st.title("Public Schedule")

share_token = st.query_params.get("token")

if not share_token:
    st.error("No schedule token provided.")
    st.stop()

schedule = get_public_schedule(share_token)

if not schedule:
    st.error("Schedule not found. The link may be invalid or sharing has been disabled.")
    st.stop()

username = schedule.get("username", "User")
current_energy = float(schedule.get("current_energy", 0.0))
tasks = schedule.get("tasks", [])

st.subheader(f"{username}'s Schedule")

st.metric("Current Energy", f"{current_energy:.1f} / 10")

st.divider()

if not tasks:
    st.info("No tasks scheduled.")
else:
    planned = [t for t in tasks if t.get("status") == "planned"]
    completed = [t for t in tasks if t.get("status") == "completed"]

    if planned:
        st.subheader("Planned Tasks")
        for task in planned:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{task['title']}**")
                    if task.get("description"):
                        st.caption(task["description"])
                with col2:
                    st.write(f"Energy: {task['energy_cost']:.1f}")
                    scheduled = task.get("scheduled_time", "")
                    if scheduled:
                        st.caption(scheduled[:16].replace("T", " "))

    if completed:
        st.subheader("Completed Tasks")
        for task in completed:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"~~{task['title']}~~")
                    if task.get("description"):
                        st.caption(task["description"])
                with col2:
                    st.write(f"Energy: {task['energy_cost']:.1f}")
