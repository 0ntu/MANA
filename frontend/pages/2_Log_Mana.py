import streamlit as st
from services.mana_service import get_mana_level, log_mana

st.title("⚡ Log Your Energy")

user_id = "u1" 
mana = get_mana_level(user_id)


st.subheader("How are you feeling right now?")
st.write("Consider the following:")
st.markdown("""
- How is your focus/concentration?
- How is your physical energy?
- How stressed do you feel about upcoming tasks?
""")

level = st.slider("Mana Level", 1, 10, mana["current"])

# Descriptive feedback based on level
if level <= 3:
    st.error("Very Low — You should take a significant break before continuing.")
elif level <= 5:
    st.warning("Low — Consider a short break or lighter tasks.")
elif level <= 7:
    st.info("Moderate — You're okay to continue but monitor your energy.")
else:
    st.success("High — Great time to tackle your hardest tasks!")

if st.button("Log Mana"):
    log_mana(user_id, level)
    st.success(f"Logged mana level: {level}/10")

# Mana history
st.divider()
st.subheader("Recent Mana Log")
history = [
    {"time": "9:00 AM", "level": 8},
    {"time": "1:00 PM", "level": 5},
    {"time": "6:00 PM", "level": 3},
]
for entry in history:
    st.write(f"🕐 {entry['time']} — ⚡ {entry['level']}/10")