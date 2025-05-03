import streamlit as st
from utils import load

st.set_page_config(page_title="Sleep App", page_icon="💤")
st.title("💤 Sleep Tracker - Dashboard")

df = load()
if len(df):
    st.metric("Total nights logged", len(df))
    st.metric("Average duration (h)", round(df["sleep_duration"].mean(), 2))
else:
    st.info("No data yet – go to **Input** to add your first record!")
