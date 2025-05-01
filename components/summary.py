import streamlit as st


def display_summary(df):
    st.subheader("📊 Sleep Summary")

    if df.empty:
        st.info("No data to summarize.")
        return

    avg_sleep = round(df["duration"].mean(), 2)
    max_sleep = round(df["duration"].max(), 2)
    min_sleep = round(df["duration"].min(), 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Sleep", f"{avg_sleep} h")
    col2.metric("Longest Sleep", f"{max_sleep} h")
    col3.metric("Shortest Sleep", f"{min_sleep} h")
