# components/sleep_form.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from utils import append


def sleep_entry_form():
    """
    • On the first visit of each LOCAL day, pre-fill:
        wake = now, sleep = now-8 h  (Asia/Taipei)
    • Thereafter, remember whatever the user picked until the next day.
    """
    tz = ZoneInfo("Asia/Taipei")
    now = datetime.now(tz).replace(second=0, microsecond=0)
    today = now.date()

    # ------------------------------------------------------------------ #
    # 1️⃣  Initialise session_state ONCE per day                          #
    # ------------------------------------------------------------------ #
    if st.session_state.get("form_date") != today:
        st.session_state["form_date"] = today
        st.session_state["sleep_end"] = now.time()
        st.session_state["sleep_start"] = (now - timedelta(hours=8)).time()
        # keep previous slider choices if they exist; otherwise set nice defaults
        st.session_state.setdefault("phys", 80)
        st.session_state.setdefault("ment", 75)
        st.session_state.setdefault("cycle", 4)
        st.session_state.setdefault("score", 70)

    # ------------------------------------------------------------------ #
    # 2️⃣  Build the form (all widgets use keys)                          #
    # ------------------------------------------------------------------ #
    st.subheader("➕  Add a new sleep record (GMT+8) for todady")

    col1, col2 = st.columns([4, 3])
    col1.markdown(
        "**Note:** If you want to enter data for earlier dates, go to")
    col2.page_link("pages/2_📜_History.py", label="History 📜")

    with st.form("new_sleep"):
        c1, c2 = st.columns(2)
        start_time = c1.time_input("Sleep time",
                                   key="sleep_start")
        end_time = c2.time_input("Wake time",
                                 key="sleep_end")

        phys = st.slider("Physical recovery %", 0, 100, key="phys")
        ment = st.slider("Mental recovery %",   0, 100, key="ment")
        cycle = st.selectbox("Sleep cycles (REM count)", [
                             1, 2, 3, 4, 5], key="cycle")
        score = st.slider("Sleep score", 0, 100, key="score")

        submitted = st.form_submit_button("Save ✅")

    # ------------------------------------------------------------------ #
    # 3️⃣  Persist on save                                                #
    # ------------------------------------------------------------------ #
    if submitted:
        start_dt = datetime.combine(today, start_time, tz)
        end_dt = datetime.combine(today, end_time,   tz)
        if start_dt > end_dt:      # crosses midnight
            start_dt -= timedelta(days=1)

        duration_h = round((end_dt - start_dt).total_seconds() / 3600, 2)

        df = pd.DataFrame([{
            "start_time":        start_dt.replace(tzinfo=None),
            "end_time":          end_dt.replace(tzinfo=None),
            "physical_recovery": phys,
            "mental_recovery":   ment,
            "sleep_cycle":       cycle,
            "sleep_score":       score,
            "sleep_duration":    duration_h,
            "create_time":       datetime.now(tz).replace(tzinfo=None),
            "update_time":       datetime.now(tz).replace(tzinfo=None),
        }])

        append(df)
        st.success(f"Saved ✅ — slept {duration_h:.2f} h")
