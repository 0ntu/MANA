import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from services.event_service import get_tasks, finish_task

token = st.session_state.get("token")
if not token:
    st.warning("Please sign up / log in first.")
    st.stop()

st.title("Today's Schedule")

est = ZoneInfo("America/New_York")
now = datetime.now(est)
st.caption(f"🕐 {now.strftime('%A, %B %d • %I:%M %p')}")

try:
    all_tasks = get_tasks(token)
except Exception as e:
    st.error(f"Failed to load tasks: {e}")
    st.stop()

today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

today_tasks = []
for task in all_tasks:
    scheduled_str = task["scheduled_time"].replace("Z", "+00:00")
    scheduled_time = datetime.fromisoformat(scheduled_str)
    if scheduled_time.tzinfo is None:
        scheduled_time = scheduled_time.replace(tzinfo=est)
    else:
        scheduled_time = scheduled_time.astimezone(est)
    if today_start <= scheduled_time <= today_end:
        task["_scheduled_dt"] = scheduled_time
        today_tasks.append(task)

today_tasks.sort(key=lambda t: t["_scheduled_dt"])

if not today_tasks:
    st.info("No tasks scheduled for today.")
    st.stop()

planned_tasks = [t for t in today_tasks if t["status"] == "planned"]
completed_tasks = [t for t in today_tasks if t["status"] == "completed"]

total_energy = sum(t["energy_cost"] for t in today_tasks)
remaining_energy = sum(t["energy_cost"] for t in planned_tasks)

col1, col2, col3 = st.columns(3)
col1.metric("📝 Total Tasks", len(today_tasks))
col2.metric("⌛ Remaining", len(planned_tasks))
col3.metric("⚡ Energy Needed", f"{remaining_energy:.1f}")

st.divider()

if planned_tasks:
    st.subheader("Planned")
    for task in planned_tasks:
        time_str = task["_scheduled_dt"].strftime("%I:%M %p")
        with st.container():
            col_time, col_info, col_action = st.columns([1, 3, 1])
            with col_time:
                st.markdown(f"**{time_str}**")
            with col_info:
                st.markdown(f"**{task['title']}**")
                if task.get("description"):
                    st.caption(task["description"])
                st.caption(f"Energy: {task['energy_cost']:.1f}")
            with col_action:
                if st.button("Done", key=f"done_{task['id']}"):
                    try:
                        finish_task(token, task["id"])
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        st.divider()

if completed_tasks:
    st.subheader("Completed")
    for task in completed_tasks:
        time_str = task["_scheduled_dt"].strftime("%I:%M %p")
        with st.container():
            col_time, col_info = st.columns([1, 4])
            with col_time:
                st.markdown(f"~~{time_str}~~")
            with col_info:
                st.markdown(f"~~{task['title']}~~")
                st.caption(f"Energy: {task['energy_cost']:.1f}")
        st.divider()