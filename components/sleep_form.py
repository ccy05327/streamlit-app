import streamlit as st
from datetime import datetime, timedelta


def display_form():
    st.subheader("📝 Log Sleep Entry")
    with st.form("sleep_form"):
        date = st.date_input("Date", value=datetime.today())
        sleep_time = st.time_input("Sleep Time", value=datetime.now().time())
        wake_time = st.time_input("Wake Time", value=(
            datetime.now() + timedelta(hours=8)).time())
        mood = st.selectbox("Mood", ["😊", "😐", "😔", "😵"])

        submitted = st.form_submit_button("Add Entry")
        if submitted:
            st.success(f"✅ Sleep logged for {date}")
            # NOTE: Currently not writing anywhere. You can add file/database logic here later.
