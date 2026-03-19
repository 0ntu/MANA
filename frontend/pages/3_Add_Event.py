import streamlit as st
from services.event_service import add_event
from datetime import date, time, datetime

st.title("📅 Add Event")

title = st.text_input("Event Title")
description = st.text_area("Description (optional)")
event_date = st.date_input("Date", value=date.today())
event_time = st.time_input("Time", value=time(9, 0))
energy_cost = st.slider("Energy Cost", 0.0, 10.0, 3.0, step=0.5)

if st.button("Add Event"):
    if title:
        scheduled_time = datetime.combine(event_date, event_time).isoformat()
        add_event("u1", {
            "title": title,
            "description": description,
            "scheduled_time": scheduled_time,
            "energy_cost": energy_cost,
        })
        st.success(f"Added: {title}")
    else:
        st.warning("Please enter an event title.")