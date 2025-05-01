import streamlit as st
import pandas as pd


def display_sidebar(df):
    st.sidebar.header("📅 Filter Sleep Data")

    # Get date range
    min_date = df["sleep_time"].dt.date.min()
    max_date = df["sleep_time"].dt.date.max()

    start_date = st.sidebar.date_input(
        "Start date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.sidebar.date_input(
        "End date", min_value=min_date, max_value=max_date, value=max_date)

    # Mood filter (optional if moods are included later)
    unique_moods = df["mood"].dropna().unique().tolist()
    selected_moods = st.sidebar.multiselect(
        "Filter by Mood", options=unique_moods, default=unique_moods)

    # Duration filter
    min_dur = float(df["duration"].min())
    max_dur = float(df["duration"].max())
    selected_dur = st.sidebar.slider("Sleep Duration Range (hours)", min_value=min_dur, max_value=max_dur,
                                     value=(min_dur, max_dur), step=0.5)

    # Apply filters
    filtered_df = df.copy()
    filtered_df = filtered_df[(df["sleep_time"].dt.date >= start_date) & (
        df["sleep_time"].dt.date <= end_date)]
    filtered_df = filtered_df[(df["duration"] >= selected_dur[0]) & (
        df["duration"] <= selected_dur[1])]

    if unique_moods:
        filtered_df = filtered_df[filtered_df["mood"].isin(selected_moods)]

    return filtered_df
