import streamlit as st
import pandas as pd
import plotly.express as px

from utils.heart_stress_loader import load_heart_data, load_stress_data

st.set_page_config(page_title="Heart & Stress Data", layout="wide")

st.title("❤️ Vitals Overview")

# Load data
heart_df = load_heart_data()
stress_df = load_stress_data()

# --- Heart Rate Section ---
st.header("💓 Heart Rate Trends")
if heart_df.empty:
    st.warning("No heart rate data available.")
else:
    st.dataframe(heart_df.sort_values(
        by="time", ascending=False), use_container_width=True)
    fig_hr = px.line(heart_df, x="time", y="heart_rate",
                     title="Heart Rate Over Time")
    st.plotly_chart(fig_hr, use_container_width=True)

# --- Stress Section ---
st.header("😰 Stress Level Trends")
if stress_df.empty:
    st.warning("No stress data available.")
else:
    st.dataframe(stress_df.sort_values(by="start_time",
                 ascending=False), use_container_width=True)
    fig_stress = px.bar(stress_df, x="start_time",
                        y="score", title="Stress Score by Hour")
    st.plotly_chart(fig_stress, use_container_width=True)
