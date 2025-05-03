# components/sleep_form.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils import append
from utils.auth import check_password

# ── configurable defaults ───────────────────────────────────────────
DEF_PHYS = 80
DEF_MENT = 75
DEF_CYCLE = 4          # value in the list [1,2,3,4,5]
DEF_SCORE = 70


def sleep_entry_form() -> None:
    """
    • First visit of each LOCAL day → pre-fill Wake = now, Sleep = now - 8 h
    • Widgets remember edits until the next day
    • Saving is gated by a one-time password prompt
    """
    tz = ZoneInfo("Asia/Taipei")
    now = datetime.now(tz).replace(second=0, microsecond=0)
    today = now.date()

    # ── 1️⃣ reset per-day defaults ───────────────────────────────────
    if st.session_state.get("form_date") != today:
        st.session_state.update(
            form_date=today,
            sleep_end=now.time(),
            sleep_start=(now - timedelta(hours=8)).time(),
            phys=st.session_state.get("phys", DEF_PHYS),
            ment=st.session_state.get("ment", DEF_MENT),
            cycle=st.session_state.get("cycle", DEF_CYCLE),
            score=st.session_state.get("score", DEF_SCORE),
        )

    # ── 2️⃣ build the form ───────────────────────────────────────────
    st.subheader("➕  Add a new sleep record (GMT+8) for today")

    text, link = st.columns([2, 5])
    text.markdown("**Note:** For earlier dates, go to")
    link.page_link("pages/2_📜_History.py", label="History 📜")

    with st.form("new_sleep"):
        c1, c2 = st.columns(2)
        start_time = c1.time_input("Sleep time", key="sleep_start")
        end_time = c2.time_input("Wake time",  key="sleep_end")

        phys = st.slider("Physical recovery %", 0, 100, key="phys")
        ment = st.slider("Mental recovery %",   0, 100, key="ment")
        cycle = st.selectbox("Sleep cycles (REM count)",
                             [1, 2, 3, 4, 5],
                             key="cycle")
        score = st.slider("Sleep score", 0, 100, key="score")

        submitted = st.form_submit_button("Save ✅")


# ------------------------------------------------------------------ #
# 3️⃣  Persist on save  (one-time password gate)                      #
# ------------------------------------------------------------------ #
if submitted:
    start_dt = datetime.combine(today, start_time, tz)
    end_dt = datetime.combine(today, end_time,   tz)
    if start_dt > end_dt:
        start_dt -= timedelta(days=1)

    duration_h = round((end_dt - start_dt).total_seconds() / 3600, 2)

    st.session_state["pending_df"] = pd.DataFrame([{
        "start_time":  start_dt.replace(tzinfo=None),
        "end_time":    end_dt.replace(tzinfo=None),
        "physical_recovery": phys,
        "mental_recovery":   ment,
        "sleep_cycle":       cycle,
        "sleep_score":       score,
        "sleep_duration":    duration_h,
        "create_time":       now.replace(tzinfo=None),
        "update_time":       now.replace(tzinfo=None),
    }])

# try to write if a pending save exists
if (df := st.session_state.get("pending_df")) is not None:
    if check_password("input-save", prompt="🔒 Password to save"):
        append(df)
        st.session_state.pop("pending_df")
        st.success(f"Saved ✅ — slept {df['sleep_duration'].iloc[0]:.2f} h")
