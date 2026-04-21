import streamlit as st
from datetime import date, datetime, time

from services.event_service import add_event

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

.add-root { font-family: 'DM Sans', sans-serif; }

.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #666;
    margin: 1.1rem 0 0.4rem 0;
}

.energy-preview {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 0.4rem;
}
.energy-dot {
    font-size: 0.9rem;
}
.energy-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #888;
}
.energy-val {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    font-weight: 500;
    color: #f0f0f0;
}

.ebar-wrap {
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    height: 8px;
    width: 100%;
    margin: 0.5rem 0 0 0;
    overflow: hidden;
}
.ebar-fill {
    height: 100%;
    border-radius: 999px;
}
.ebar-fill.low  { background: #06D6A0; }
.ebar-fill.mid  { background: #FFD166; }
.ebar-fill.high { background: #FF6B6B; }

.success-box {
    background: rgba(6,214,160,0.1);
    border: 1px solid rgba(6,214,160,0.25);
    border-radius: 10px;
    padding: 0.85rem 1rem;
    color: #06D6A0;
    font-size: 0.88rem;
    margin-top: 0.5rem;
}
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="add-root">', unsafe_allow_html=True)
st.title("Add Task")

token = st.session_state.get("token")
if not token:
    st.warning("Please sign up / log in first.")
    st.stop()
st.markdown("<div class='section-label'>Task Details</div>", unsafe_allow_html=True)
title = st.text_input("Title", placeholder="e.g. Study for exam")

col1, col2 = st.columns(2)
with col1:
    event_date = st.date_input("Date", value=date.today())
with col2:
    event_time = st.time_input("Time", value=time(9, 0))

description = st.text_area("Description (optional)", placeholder="Any notes...", height=80)

st.markdown("<div class='section-label'>Energy Cost</div>", unsafe_allow_html=True)
energy_cost = st.slider("", 0.0, 10.0, 3.0, step=0.5, label_visibility="collapsed")

# energy cost preview
if energy_cost >= 7:
    dot, state, label = "🔴", "high", "High drain"
elif energy_cost >= 4:
    dot, state, label = "🟡", "mid", "Medium drain"
else:
    dot, state, label = "🟢", "low", "Low drain"

pct = (energy_cost / 10.0) * 100
st.markdown(f"""
<div class='card'>
    <div class='energy-preview'>
        <span class='energy-dot'>{dot}</span>
        <span class='energy-val'>{energy_cost:.1f}</span>
        <span class='energy-label'>/ 10 &nbsp;·&nbsp; {label}</span>
    </div>
    <div class='ebar-wrap'><div class='ebar-fill {state}' style='width:{pct}%'></div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-label'>Recurrence</div>", unsafe_allow_html=True)
recurring = st.checkbox("Repeat daily")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("Add Task", use_container_width=True, type="primary"):
    if not title.strip():
        st.warning("Please enter a task title.")
        st.stop()

    scheduled_dt = datetime.combine(event_date, event_time)
    payload = {
        "title": title.strip(),
        "description": description.strip(),
        "scheduled_time": scheduled_dt.isoformat(),
        "energy_cost": float(energy_cost),
        "is_recurring": bool(recurring),
        "repeat_pattern": "daily" if recurring else None,
    }

    try:
        add_event(token, payload)
        st.markdown(f"<div class='success-box'>✓ &nbsp;<strong>{title.strip()}</strong> added for {scheduled_dt.strftime('%b %d at %I:%M %p')}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not add task: {e}")

st.markdown('</div>', unsafe_allow_html=True)