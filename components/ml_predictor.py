import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pandas as pd


def extract_features(df):
    df = df.copy()
    df["sleep_hour"] = df["sleep_time"].dt.hour
    df["sleep_minute"] = df["sleep_time"].dt.minute
    df["weekday"] = df["sleep_time"].dt.weekday  # 0 = Monday
    df["month"] = df["sleep_time"].dt.month
    df["start_minutes"] = df["sleep_hour"] * 60 + df["sleep_minute"]

    features = df[["start_minutes", "weekday", "month"]]
    target = df["duration"]

    return features, target


def train_model(X, y):
    model = RandomForestRegressor(random_state=42, n_estimators=100)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    score = r2_score(y_test, y_pred)
    error = mean_absolute_error(y_test, y_pred)

    return model, score, error


def display_predictor(df):
    st.subheader("🤖 Sleep Duration Predictor")

    if df.empty:
        st.info("Not enough data to train a model.")
        return

    # Extract features
    X, y = extract_features(df)

    # Train model
    model, score, error = train_model(X, y)

    # Display performance
    st.markdown(f"**Model R² Score**: {score:.2f}")
    st.markdown(f"**Mean Absolute Error**: {error:.2f} hours")

    st.markdown("### 📅 Predict Your Sleep Duration")

    # Prediction inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        hour = st.slider("Sleep Hour", 0, 23, 23)
    with col2:
        minute = st.slider("Sleep Minute", 0, 59, 30)
    with col3:
        weekday = st.selectbox("Days of the Week", options=list(range(7)), format_func=lambda x: [
                               "Monday", "Tuesday", "Wedesday", "Thursday", "Friday", "Saturday", "Sunday"][x])

        month = st.selectbox("Month", options=list(range(1, 13)), format_func=lambda x: [
                            "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][x-1])

    # Prepare input
    input_features = pd.DataFrame([{
        "start_minutes": hour * 60 + minute,
        "weekday": weekday,
        "month": month
    }])

    prediction = model.predict(input_features)[0]
    st.success(f"🕒 Predicted Sleep Duration: **{prediction:.2f} hours**")
