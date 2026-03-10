import streamlit as st
from services.event_service import add_event
from datetime import date

st.title("Add Event")

title = st.text_input("Event Title")
event_date = st.date_input("Date", value=date.today())
energy_cost = st.slider("Energy Cost", 1, 10, 3)
recurring = st.checkbox("Recurring event?")

if st.button("Add Event"):
    if title:
        add_event("u1", {
            "title": title,
            "date": str(event_date),
            "energy_cost": energy_cost,
            "recurring": recurring
        })
        st.success(f"Added: {title}")
    else:
        st.warning("Please enter an event title.")