import pandas as pd


def load_samsung_sleep_data(path="data/samsung health sleep combined data.csv"):
    df = pd.read_csv(path)

    # Convert to datetime
    df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
    df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")

    # Create useful columns
    df["sleep_date"] = df["start_time"].dt.date
    df["weekday"] = df["start_time"].dt.day_name()
    df["duration_hr"] = pd.to_numeric(
        df["sleep_duration"], errors="coerce") / 60

    return df[[
        "sleep_date", "weekday", "start_time", "end_time", "duration_hr",
        "sleep_score", "mental_recovery", "physical_recovery", "sleep_cycle"
    ]]
