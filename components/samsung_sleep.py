import streamlit as st
import plotly.express as px
import pandas as pd


def display_samsung_sleep(df: pd.DataFrame):
    st.header("📊 Sleep Quality Tracker (Samsung Data)")

    if df.empty:
        st.info("No Samsung sleep data available.")
        return

    # Optional filters
    with st.expander("🔍 Filter by Date or Weekday"):
        col1, col2 = st.columns(2)
        with col1:
            min_date = df["sleep_date"].min()
            max_date = df["sleep_date"].max()
            selected_range = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        with col2:
            weekday_order = ["Monday", "Tuesday", "Wednesday",
                             "Thursday", "Friday", "Saturday", "Sunday"]
            present_days = sorted(
                df["weekday"].dropna().unique(), key=weekday_order.index)

            selected_days = st.multiselect(
                "Weekdays", options=present_days, default=present_days)

    # Apply filters
    filtered = df.copy()
    if isinstance(selected_range, tuple):
        filtered = filtered[
            (filtered["sleep_date"] >= selected_range[0]) &
            (filtered["sleep_date"] <= selected_range[1])
        ]
    filtered = filtered[filtered["weekday"].isin(selected_days)]

    # Summary
    st.subheader("📈 Summary Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Duration", f"{filtered['duration_hr'].mean():.2f} h")
    col2.metric("Avg Sleep Score", f"{filtered['sleep_score'].mean():.1f}")
    col3.metric("Avg Sleep Cycles", f"{filtered['sleep_cycle'].mean():.1f}")

    # Plotly chart
    st.subheader("🛏️ Sleep Score Over Time")
    fig = px.line(
        filtered,
        x="sleep_date",
        y="sleep_score",
        markers=True,
        hover_data=["duration_hr", "mental_recovery",
                    "physical_recovery", "sleep_cycle"],
        title="Sleep Score Trend"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Display table
    with st.expander("📋 View Full Table", expanded=False):
        st.dataframe(
            filtered.sort_values(by="start_time", ascending=False),
            use_container_width=True
        )
