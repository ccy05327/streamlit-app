import streamlit as st
import plotly.express as px


def display_chart(df):
    st.subheader("📈 Sleep Timeline")

    if df.empty:
        st.warning("No data to display.")
        return

    # Add string date for grouping/tooltip
    df["date_str"] = df["sleep_time"].dt.strftime("%Y-%m-%d")

    fig = px.timeline(
        df,
        x_start="sleep_time",
        x_end="wake_time",
        y="date_str",
        color="duration",
        labels={"date_str": "Date"},
        color_continuous_scale="Blues",
        hover_data={"sleep_time": True, "wake_time": True, "duration": True},
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=500, margin=dict(t=20, b=20))

    st.plotly_chart(fig, use_container_width=True)
