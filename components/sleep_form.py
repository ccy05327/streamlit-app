import streamlit as st
import pandas as pd
from utils import append


def sleep_entry_form():
    st.subheader("➕  Add a new sleep record")

    with st.form("new_sleep"):
        c1, c2 = st.columns(2)
        start = c1.time_input("Sleep time")
        end = c2.time_input("Wake time")
        phys = st.slider("Physical recovery %", 0, 100, 80)
        ment = st.slider("Mental recovery %",   0, 100, 75)
        cycle = st.selectbox("Sleep cycle (# of REMs)", [3, 4, 5], index=1)
        score = st.slider("Sleep score", 0, 100, 70)
        submit = st.form_submit_button("Save ✅")

    if submit:
        df = pd.DataFrame([{
            "start_time":  pd.Timestamp.combine(pd.Timestamp.utcnow().date(), start),
            "end_time":    pd.Timestamp.combine(pd.Timestamp.utcnow().date(), end),
            "physical_recovery": phys,
            "mental_recovery":   ment,
            "sleep_cycle":       cycle,
            "sleep_score":       score,
            "sleep_duration":    (pd.Timestamp.combine(pd.Timestamp.utcnow().date(), end) -
                                  pd.Timestamp.combine(pd.Timestamp.utcnow().date(), start)).seconds / 3600,
            "create_time":       pd.Timestamp.utcnow(),
        }])
        append(df)
        st.success("Saved 🎉")
