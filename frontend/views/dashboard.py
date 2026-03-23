from __future__ import annotations

import requests
import streamlit as st

from services.auth_service import BACKEND_URL, build_auth_headers


st.title("Dashboard Summary")

token = st.session_state.get("token")
if not token:
    st.warning("Please sign up / log in first.")
    st.stop()

try:
    resp = requests.get(
        f"{BACKEND_URL}/dashboard/summary",
        headers=build_auth_headers(token),
        timeout=20,
    )
    data = resp.json()
except Exception as e:
    st.error(f"Failed to load dashboard summary: {e}")
    st.stop()

if resp.status_code >= 400:
    st.error(data.get("detail") or "Dashboard summary request failed.")
    st.stop()

remaining_cost = float(data.get("remaining_today_energy_cost", 0.0))
current_energy = float(data.get("current_energy", 0.0))
estimated_end = float(data.get("estimated_end_of_day_energy", 0.0))

planned_tasks_count = int(data.get("planned_tasks_count", 0))
completed_tasks_count = int(data.get("completed_tasks_count", 0))
remaining_today_tasks_amount = int(data.get("remaining_today_tasks_amount", 0))

stress = data.get("mana_stress")

st.metric("Current Mana / Energy", f"{current_energy:.1f}")
st.metric("Planned Energy Cost Today", f"{remaining_cost:.1f}")
st.metric("Estimated End-of-Day Energy", f"{estimated_end:.1f}")
if stress is not None:
    st.metric("Load stress", f"{float(stress):.1f} / 10")

st.subheader("Task Status")
col1, col2, col3 = st.columns(3)
col1.metric("Planned Tasks", planned_tasks_count)
col2.metric("Completed Tasks", completed_tasks_count)
col3.metric("Remaining Today", remaining_today_tasks_amount)

tip = data.get("scheduling_tip")
if data.get("overload_warning"):
    st.error("Your planned stuff costs more mana than you have right now.")
if tip:
    st.info(tip)
elif estimated_end <= 2.0:
    st.warning("Might be rough later today — maybe move something.")
elif current_energy <= 2.0:
    st.info("Starting low — go easy.")
else:
    st.success("Roughly okay for now.")

