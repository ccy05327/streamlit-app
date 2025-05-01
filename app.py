import streamlit as st
from components import sidebar, sleep_form, summary, plot
from utils.data_loader import load_sleep_data


st.set_page_config(page_title="Sleep Tracker", layout="wide")

# Sidebar
df = load_sleep_data("data/sleep_data.json")
filtered_df = sidebar.display_sidebar(df)


# Main sections
st.title("🌙 Sleep Tracker Dashboard")
sleep_form.display_form()
summary.display_summary(filtered_df)
plot.display_chart(filtered_df)
