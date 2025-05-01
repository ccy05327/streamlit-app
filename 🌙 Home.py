import streamlit as st
import pandas as pd
import plotly.express as px

from utils.samsung_loader import load_samsung_sleep_data
from utils.heart_stress_loader import load_heart_data, load_stress_data

st.set_page_config(page_title="Home", page_icon="🌙", layout="wide")

st.title("📱 Samsung Health Dashboard")

st.markdown("""
Welcome to your all-in-one health data dashboard! 💖
Here you'll find:
- 🛏️ Detailed sleep tracking
- ❤️ Heart rate trends
- 😰 Stress level patterns

Use the sidebar to navigate between pages or explore your insights below.
""")

# Load Data
sleep_df = load_samsung_sleep_data()
heart_df = load_heart_data()
stress_df = load_stress_data()

# --- High-Level Summary ---
st.header("📊 Quick Overview")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Latest Sleep Score",
              f"{sleep_df['sleep_score'].dropna().iloc[-1]}")
with col2:
    st.metric("Last Heart Rate",
              f"{heart_df['heart_rate'].dropna().iloc[-1]} bpm")
with col3:
    st.metric("Recent Stress Score", f"{stress_df['score'].dropna().iloc[-1]}")

st.markdown("---")
st.markdown(
    "Use the navigation sidebar to explore more in-depth views of your health data.")
