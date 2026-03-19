import requests
import streamlit as st

from services.auth_service import BACKEND_URL, build_auth_headers


st.title("Log Mana / Energy")

token = st.session_state.get("token")
if not token:
    st.warning("Please sign up / log in first.")
    st.stop()

energy_level = st.slider("Current energy (mana)", 0.0, 10.0, 7.0, step=0.5)

if st.button("Log Energy"):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/energy/log",
            json={"energy_level": float(energy_level)},
            headers=build_auth_headers(token),
            timeout=20,
        )
        data = resp.json()
    except Exception as e:
        st.error(f"Failed to log energy: {e}")
    else:
        if resp.status_code >= 400:
            st.error(data.get("detail") or "Energy log failed.")
        else:
            st.success("Energy logged.")
            st.json(data)

