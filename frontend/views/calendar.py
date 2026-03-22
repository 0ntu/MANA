import calendar
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from services.event_service import get_tasks

st.title("📅 Monthly Overview")

token = st.session_state.get("token")
if not token:
    st.warning("Please sign up / log in first.")
    st.stop()

# Use EST so today matches the user's timezone, not Docker's UTC
today = datetime.now(ZoneInfo("America/New_York")).date()

if "cal_month" not in st.session_state:
    st.session_state.cal_month = today.month
if "cal_year" not in st.session_state:
    st.session_state.cal_year = today.year

# Month navigation
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("Prev"):
        if st.session_state.cal_month == 1:
            st.session_state.cal_month = 12
            st.session_state.cal_year -= 1
        else:
            st.session_state.cal_month -= 1
with col2:
    month_label = datetime(st.session_state.cal_year, st.session_state.cal_month, 1).strftime("%B %Y")
    st.markdown(f"<h3 style='text-align:center'>{month_label}</h3>", unsafe_allow_html=True)
with col3:
    if st.button("Next"):
        if st.session_state.cal_month == 12:
            st.session_state.cal_month = 1
            st.session_state.cal_year += 1
        else:
            st.session_state.cal_month += 1

year = st.session_state.cal_year
month = st.session_state.cal_month

# Fetch and group tasks by day
tasks_by_day = {}
try:
    all_tasks = get_tasks(token)
    for task in all_tasks:
        scheduled_str = task.get("scheduled_time", "").replace("Z", "+00:00")
        if not scheduled_str:
            continue
        task_date = datetime.fromisoformat(scheduled_str).date()
        if task_date.year == year and task_date.month == month:
            tasks_by_day.setdefault(task_date.day, []).append(task)
except Exception as e:
    st.error(f"Failed to load tasks: {e}")
    st.stop()

# Calendar grid
day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
header_cols = st.columns(7)
for i, h in enumerate(day_headers):
    header_cols[i].markdown(f"**{h}**")

for week in calendar.monthcalendar(year, month):
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day == 0:
                st.markdown("&nbsp;", unsafe_allow_html=True)
                continue

            is_today = (day == today.day and month == today.month and year == today.year)
            st.markdown(f"**🔵 {day}**" if is_today else f"**{day}**")

            for task in tasks_by_day.get(day, []):
                energy = task.get("energy_cost", 0)
                dot = "🔴" if energy >= 7 else "🟡" if energy >= 4 else "🟢"
                completed = task.get("status") == "completed"
                label = f"<s>{task['title']}</s>" if completed else task['title']
                st.markdown(f"<small>{dot} {label}</small>", unsafe_allow_html=True)

st.divider()
st.markdown("<small>🟢 Low energy &nbsp; 🟡 Medium energy &nbsp; 🔴 High energy &nbsp; 🔵 Today &nbsp; <s>title</s> = completed</small>", unsafe_allow_html=True)