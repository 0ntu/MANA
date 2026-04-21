import calendar
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from services.event_service import get_tasks

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

.cal-root { font-family: 'DM Sans', sans-serif; }

.cal-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
}
.cal-month-label {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-color, #e0e0e0);
}
.cal-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 4px;
    table-layout: fixed;
}
.cal-table th {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #888;
    text-align: center;
    padding: 4px 0 8px 0;
}
.cal-cell {
    vertical-align: top;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 6px 7px 8px 7px;
    min-height: 76px;
    transition: background 0.15s;
}
.cal-cell:hover {
    background: rgba(255,255,255,0.06);
}
.cal-cell.empty {
    background: transparent;
    border-color: transparent;
}
.cal-cell.today {
    border-color: #5B8EFF;
    background: rgba(91,142,255,0.08);
}
.cal-day-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    color: #aaa;
}
.cal-cell.today .cal-day-num {
    color: #5B8EFF;
    font-weight: 600;
}
.cal-task {
    display: flex;
    align-items: baseline;
    gap: 4px;
    margin-bottom: 2px;
    font-size: 0.68rem;
    line-height: 1.3;
    color: #ccc;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    max-width: 100%;
}
.cal-task.done {
    text-decoration: line-through;
    opacity: 0.45;
}
.cal-dot {
    font-size: 0.55rem;
    flex-shrink: 0;
    line-height: 1.6;
}
.cal-overflow {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: #666;
    margin-top: 2px;
}
.cal-legend {
    display: flex;
    gap: 1.25rem;
    margin-top: 1rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    color: #888;
    flex-wrap: wrap;
}
.cal-legend span { display: flex; align-items: center; gap: 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="cal-root">', unsafe_allow_html=True)
st.title("Monthly Overview")

token = st.session_state.get("token")
if not token:
    st.warning("Please sign up / log in first.")
    st.stop()

today = datetime.now(ZoneInfo("America/New_York")).date()

if "cal_month" not in st.session_state:
    st.session_state.cal_month = today.month
if "cal_year" not in st.session_state:
    st.session_state.cal_year = today.year

col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button("← Prev", use_container_width=True):
        if st.session_state.cal_month == 1:
            st.session_state.cal_month = 12
            st.session_state.cal_year -= 1
        else:
            st.session_state.cal_month -= 1
with col2:
    label = datetime(st.session_state.cal_year, st.session_state.cal_month, 1).strftime("%B %Y")
    st.markdown(
        f"<p style='text-align:center;font-family:DM Mono,monospace;"
        f"font-size:1.05rem;letter-spacing:.08em;text-transform:uppercase;"
        f"margin:6px 0 0 0'>{label}</p>",
        unsafe_allow_html=True,
    )
with col3:
    if st.button("Next →", use_container_width=True):
        if st.session_state.cal_month == 12:
            st.session_state.cal_month = 1
            st.session_state.cal_year += 1
        else:
            st.session_state.cal_month += 1

year = st.session_state.cal_year
month = st.session_state.cal_month

tasks_by_day: dict[int, list] = {}
try:
    all_tasks = get_tasks(token)
    for task in all_tasks:
        s = task.get("scheduled_time", "").replace("Z", "+00:00")
        if not s:
            continue
        d = datetime.fromisoformat(s).date()
        if d.year == year and d.month == month:
            tasks_by_day.setdefault(d.day, []).append(task)
except Exception as e:
    st.error(f"Failed to load tasks: {e}")
    st.stop()

MAX_VISIBLE = 3   # tasks shown before "+N more"

DOT = {"low": "🟢", "mid": "🟡", "high": "🔴"}

def energy_dot(cost: float) -> str:
    if cost >= 7:
        return DOT["high"]
    if cost >= 4:
        return DOT["mid"]
    return DOT["low"]

rows_html = []

# header
rows_html.append("<table class='cal-table'><thead><tr>")
for h in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
    rows_html.append(f"<th>{h}</th>")
rows_html.append("</tr></thead><tbody>")

for week in calendar.monthcalendar(year, month):
    rows_html.append("<tr>")
    for day in week:
        if day == 0:
            rows_html.append("<td class='cal-cell empty'></td>")
            continue

        is_today = (day == today.day and month == today.month and year == today.year)
        cell_class = "cal-cell today" if is_today else "cal-cell"

        day_tasks = tasks_by_day.get(day, [])
        visible = day_tasks[:MAX_VISIBLE]
        overflow = len(day_tasks) - MAX_VISIBLE

        tasks_html = ""
        for t in visible:
            dot = energy_dot(float(t.get("energy_cost", 0)))
            done = t.get("status") == "completed"
            title = t.get("title", "")[:22]
            task_class = "cal-task done" if done else "cal-task"
            tasks_html += (
                f"<div class='{task_class}'>"
                f"<span class='cal-dot'>{dot}</span>"
                f"<span>{title}</span>"
                f"</div>"
            )
        if overflow > 0:
            tasks_html += f"<div class='cal-overflow'>+{overflow} more</div>"

        rows_html.append(
            f"<td class='{cell_class}'>"
            f"<span class='cal-day-num'>{day}</span>"
            f"{tasks_html}"
            f"</td>"
        )
    rows_html.append("</tr>")

rows_html.append("</tbody></table>")

st.markdown("".join(rows_html), unsafe_allow_html=True)
st.markdown("""
<div class='cal-legend'>
  <span>🟢 Low energy</span>
  <span>🟡 Medium energy</span>
  <span>🔴 High energy</span>
  <span>🔵 Today</span>
  <span><s>title</s> completed</span>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)