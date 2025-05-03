# pages/5_📈_Charts.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils.data_io import load
from zoneinfo import ZoneInfo

st.set_page_config(page_title="📈 Charts", layout="wide")
st.title("📈 Sleep Timeline Chart")

# ── Load & filter ──────────────────────────────────────────────────────────
tz = ZoneInfo("Asia/Taipei")
df_all = load().sort_values("start_time", ascending=False)
if df_all.empty:
    st.info("No sleep data yet. Log some nights first!")
    st.stop()

# unique real dates (newest first) and slider
unique_dates = sorted(df_all["start_time"].dt.date.unique(), reverse=True)
max_days = len(unique_dates)
days = st.slider("Days to display", 1, max_days, min(30, max_days))
st.markdown(f"**Max days available:** {max_days}")
dates_shown = set(unique_dates[:days])
df_sel = df_all[df_all["start_time"].dt.date.isin(dates_shown)]

# ── 2. Build split-at-midnight segments ──────────────────────────────────
DUMMY = datetime(2025, 6, 1)
DUMMY_END = DUMMY + timedelta(days=1)

rows = []
for _, r in df_sel.iterrows():
    real_date = r["start_time"].date()
    next_date = real_date + timedelta(days=1)

    # map times onto the dummy day
    s = r["start_time"]
    e = r["end_time"]
    s_dummy = DUMMY.replace(hour=s.hour,   minute=s.minute,   second=s.second)
    e_dummy = DUMMY.replace(hour=e.hour,   minute=e.minute,   second=e.second)
    # if wake ≤ sleep: we crossed midnight
    if e_dummy <= s_dummy:
        e_dummy += timedelta(days=1)

    # if still on same dummy-day → one bar
    if e_dummy.date() == DUMMY.date():
        rows.append({
            "Date":     real_date.isoformat(),
            "Sleep":    s_dummy,
            "Wake":     e_dummy,
            "Duration": r["sleep_duration"],
        })
    else:
        # split into two bars
        # bar 1: bedtime → midnight
        rows.append({
            "Date":     real_date.isoformat(),
            "Sleep":    s_dummy,
            "Wake":     DUMMY_END,
            "Duration": r["sleep_duration"],
        })
        # bar 2: midnight → wake
        wake_dummy = DUMMY.replace(
            hour=e.hour, minute=e.minute, second=e.second)
        rows.append({
            "Date":     next_date.isoformat(),
            "Sleep":    DUMMY,
            "Wake":     wake_dummy,
            "Duration": r["sleep_duration"],
        })

df_chart = pd.DataFrame(rows)


# ── Draw Plotly timeline ──────────────────────────────────────────────────
fig = px.timeline(
    df_chart,
    x_start="Sleep",
    x_end="Wake",
    y="Date",
    color="Duration",
    color_continuous_scale=['#ade8f4', '#48cae4', '#0077b6'],
    template='plotly_dark',
)
fig.update_yaxes(autorange="reversed")

# clamp X-axis to 00:00→24:00
fig.update_xaxes(
    range=[DUMMY, DUMMY_END],
    tickformat="%H:%M",
    gridcolor='#2e2e3f'
)

# styling
fig.update_layout(
    paper_bgcolor='#1e1e2f',
    plot_bgcolor='#1e1e2f',
    font_color='#ffffff',
    margin=dict(l=20, r=20, t=40, b=20),
    height=40 * len(df_chart["Date"].unique())
)

# ── 5. Render chart ─────────────────────────────────────────────────────────
st.plotly_chart(fig, use_container_width=True)

# ── 6. Debug tables ─────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Raw sleep records for the selected days")
st.dataframe(
    df_sel.reset_index(drop=True),
    use_container_width=True,
    column_config={
        "start_time":     st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm"),
        "end_time":       st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm"),
        "sleep_duration": st.column_config.NumberColumn(format="%.2f"),
    }
)
