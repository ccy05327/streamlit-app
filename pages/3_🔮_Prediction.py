import streamlit as st
from components.ml_predictor import next_sleep_forecast

st.title("🔮 Prediction")

result = next_sleep_forecast()
if "error" in result:
    st.info(result["error"])
else:
    st.metric("Next sleep time", result["sleep"])
    st.metric("Expected wake time", result["wake"])
    st.metric("Predicted duration (h)", result["duration"])
