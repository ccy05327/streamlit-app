from components import samsung_sleep
import streamlit as st
from components import sidebar, sleep_form, summary, plot, ml_predictor, samsung_sleep
from utils.samsung_loader import load_samsung_sleep_data
from utils.data_loader import load_sleep_data


st.set_page_config(page_title="Sleep Tracker", layout="wide")

# Sidebar
df = load_sleep_data("data/sleep_data.json")
df = sidebar.display_sidebar(df)

samsung_df = load_samsung_sleep_data()

ml_predictor.display_predictor(df)

# Main sections
st.title("🌙 Sleep Tracker Dashboard")
sleep_form.display_form()
summary.display_summary(df)
plot.display_chart(df)
samsung_sleep.display_samsung_sleep(samsung_df)
