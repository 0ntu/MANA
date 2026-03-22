import streamlit as st
from datetime import date, datetime, time

from services.event_service import add_event


st.title("Add Event")

token = st.session_state.get("token")
if not token:
    st.warning("Please sign up / log in first.")
    st.stop()

title = st.text_input("Event Title")
event_date = st.date_input("Date", value=date.today())
event_time = st.time_input("Time", value=time(9, 0))
energy_cost = st.slider("Energy Cost", 1, 10, 3)
recurring = st.checkbox("Recurring event?")

if st.button("Add Event"):
    if not title.strip():
        st.warning("Please enter an event title.")
        st.stop()

    scheduled_dt = datetime.combine(event_date, event_time)

    payload = {
        "title": title.strip(),
        "description": "",
        "scheduled_time": scheduled_dt.isoformat(),
        "energy_cost": float(energy_cost),
        "recurring": bool(recurring),  # backend may ignore if not implemented
    }

    try:
        add_event(token, payload)
        st.success(f"Added: {title.strip()}")
    except Exception as e:
        st.error(f"Could not add event: {e}")