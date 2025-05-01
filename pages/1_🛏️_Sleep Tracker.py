import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_sleep_data
from utils.samsung_loader import load_samsung_sleep_data
from components import sidebar, sleep_form, summary, plot, ml_predictor

st.set_page_config(page_title="Sleep Tracker", layout="wide")

st.title("🛏️ Sleep Tracker")

# --- JSON-based Sleep Tracker ---
st.header("📓 Manual Sleep Log")
df = load_sleep_data("data/sleep_data.json")
filtered_df = sidebar.display_sidebar(df)
sleep_form.display_form()
summary.display_summary(filtered_df)
plot.display_chart(filtered_df)
ml_predictor.display_predictor(df)

st.markdown("---")

# --- Samsung Sleep Data Section ---
st.header("📱 Samsung Sleep Quality")
samsung_df = load_samsung_sleep_data()

if samsung_df.empty:
    st.info("No Samsung sleep data available.")
else:
    with st.expander("🔍 Filter by Date or Weekday"):
        col1, col2 = st.columns(2)
        with col1:
            min_date = samsung_df["sleep_date"].min()
            max_date = samsung_df["sleep_date"].max()
            selected_range = st.date_input("Date range", value=(
                min_date, max_date), min_value=min_date, max_value=max_date)
        with col2:
            weekday_order = ["Monday", "Tuesday", "Wednesday",
                             "Thursday", "Friday", "Saturday", "Sunday"]
            present_days = sorted(
                samsung_df["weekday"].dropna().unique(), key=weekday_order.index)
            selected_days = st.multiselect(
                "Weekdays", options=present_days, default=present_days)

    filtered_samsung = samsung_df.copy()
    if isinstance(selected_range, tuple):
        filtered_samsung = filtered_samsung[(filtered_samsung["sleep_date"] >= selected_range[0]) & (
            filtered_samsung["sleep_date"] <= selected_range[1])]
    filtered_samsung = filtered_samsung[filtered_samsung["weekday"].isin(
        selected_days)]

    st.subheader("📈 Sleep Score Trend")
    fig = px.line(
        filtered_samsung,
        x="sleep_date",
        y="sleep_score",
        markers=True,
        hover_data=["duration_hr", "mental_recovery",
                    "physical_recovery", "sleep_cycle"],
        title="Samsung Sleep Score Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 View Full Sleep Records"):
        st.dataframe(filtered_samsung.sort_values(
            by="start_time", ascending=False), use_container_width=True)
