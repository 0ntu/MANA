import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from zoneinfo import ZoneInfo

from services.auth_service import BACKEND_URL, build_auth_headers

st.title("Energy History")

token = st.session_state.get("token")
if not token:
    st.warning("Please sign up / log in first.")
    st.stop()

try:
    resp = requests.get(
        f"{BACKEND_URL}/energy/history",
        headers=build_auth_headers(token),
        timeout=20,
    )
    data = resp.json()
except Exception as e:
    st.error(f"Failed to load energy history: {e}")
    st.stop()

if resp.status_code >= 400:
    st.error(data.get("detail") or "Failed to load energy history.")
    st.stop()

history = data.get("history", [])

if not history:
    st.info("No energy logs yet. Log your mana level to start tracking.")
    st.stop()

est = ZoneInfo("America/New_York")
rows = []
for i, entry in enumerate(history):
    dt = datetime.fromisoformat(entry["created_time"].replace("Z", "+00:00"))
    dt = dt.astimezone(est)
    rows.append({
        "Time": dt,
        "Energy": entry["energy_level"],
        "Log #": i + 1,
    })

df = pd.DataFrame(rows)

col_filter, _ = st.columns([2, 3])
with col_filter:
    time_range = st.selectbox("Time range", ["All time", "Last 7 days", "Last 30 days"], index=0, label_visibility="collapsed")

now = datetime.now(est)
if time_range == "Last 7 days":
    df = df[df["Time"] >= now.replace(day=now.day - 7)]
elif time_range == "Last 30 days":
    df = df[df["Time"] >= now.replace(day=max(1, now.day - 30))]

if df.empty:
    st.info("No logs in this time range.")
    st.stop()

avg = df["Energy"].mean()
high = df["Energy"].max()
low = df["Energy"].min()
latest = df["Energy"].iloc[-1]

if len(df) >= 6:
    recent_avg = df["Energy"].iloc[-3:].mean()
    prev_avg = df["Energy"].iloc[-6:-3].mean()
    diff = recent_avg - prev_avg
    trend = f"↑ {diff:.1f}" if diff > 0 else f"↓ {abs(diff):.1f}"
    trend_color = "normal" if diff > 0 else "inverse"
else:
    trend = "–"
    trend_color = "off"

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Latest", f"{latest:.1f}")
c2.metric("Average", f"{avg:.1f}")
c3.metric("Peak", f"{high:.1f}")
c4.metric("Lowest", f"{low:.1f}")
c5.metric("Trend", trend, delta_color=trend_color)

st.divider()

fig = go.Figure()

fig.add_hrect(y0=0, y1=2.5,   fillcolor="rgba(255,107,107,0.08)", line_width=0, annotation_text="low",    annotation_position="left")
fig.add_hrect(y0=2.5, y1=6.0, fillcolor="rgba(255,209,102,0.08)", line_width=0, annotation_text="medium", annotation_position="left")
fig.add_hrect(y0=6.0, y1=10,  fillcolor="rgba(6,214,160,0.08)",   line_width=0, annotation_text="high",   annotation_position="left")

use_log_num = False
if len(df) > 1:
    time_span = (df["Time"].iloc[-1] - df["Time"].iloc[0]).total_seconds()
    use_log_num = time_span < 3600

x_vals = df["Log #"] if use_log_num else df["Time"]
x_label = "Log #" if use_log_num else "Time"

point_colors = []
for e in df["Energy"]:
    if e <= 2.5:
        point_colors.append("#FF6B6B")
    elif e <= 6.0:
        point_colors.append("#FFD166")
    else:
        point_colors.append("#06D6A0")

fig.add_trace(go.Scatter(
    x=x_vals,
    y=df["Energy"],
    mode="lines+markers",
    line=dict(color="#5B8EFF", width=2.5),
    marker=dict(
        color=point_colors,
        size=9,
        line=dict(color="#1a1a1a", width=1.5),
    ),
    hovertemplate=(
        f"<b>%{{y:.1f}}</b> mana<br>"
        f"{x_label}: %{{x}}<extra></extra>"
    ),
))

fig.update_layout(
    xaxis_title=x_label,
    yaxis_title="Energy Level",
    yaxis=dict(range=[0, 10.5], dtick=2),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#aaa"),
    margin=dict(l=40, r=20, t=20, b=40),
    height=340,
    showlegend=False,
    hovermode="x unified",
)
fig.update_xaxes(showgrid=False, zeroline=False)
fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False)

st.plotly_chart(fig, use_container_width=True)

st.caption(f"{len(df)} log{'s' if len(df) != 1 else ''} shown · {time_range.lower()}")