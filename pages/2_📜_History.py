import streamlit as st
import altair as alt
from utils import load

st.title("📜 History")

df = load()
st.dataframe(df, use_container_width=True, hide_index=True)

if len(df):
    st.subheader("Timeline")
    c = alt.Chart(df).mark_bar().encode(
        x="start_time:T",
        x2="end_time:T",
        y=alt.Y("row_number():N", axis=None),
        tooltip=["start_time", "end_time", "sleep_duration"]
    ).properties(height=200)
    st.altair_chart(c, use_container_width=True)
