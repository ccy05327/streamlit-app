# pages/3_🔮_Prediction.py
import streamlit as st
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from components.ml_predictor import next_sleep_forecast, forecast_for_date

# ——————————————————————————————————————————————————————————————————————————
# Configuration
# — use Asia/Taipei for “today” and all date logic
tz = ZoneInfo("Asia/Taipei")
today = datetime.now(tz).date()

st.title("🔮 Sleep Prediction")


# ── Date picker ─────────────────────────────────────────────────────────────
sel_date = st.date_input(
    "Select a future date",
    value=today + timedelta(days=1),
    min_value=today + timedelta(days=1),
    help="Pick tomorrow or any later date to see the forecast."
)

# ── Compute forecast ───────────────────────────────────────────────────────
if sel_date == today + timedelta(days=1):
    result = next_sleep_forecast()
else:
    result = forecast_for_date(sel_date)

# ── Display ────────────────────────────────────────────────────────────────
if "error" in result:
    st.info(result["error"])
else:
    st.subheader(f"Forecast for **{result['date']}**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Sleep time", result["sleep"])
    c2.metric("Wake time",  result["wake"])
    c3.metric("Duration (h)", result["duration"])
