import pandas as pd


def load_heart_data(path="data/samsung health heart rate data.csv"):
    try:
        df = pd.read_csv(path)
        df["time"] = pd.to_datetime(
            df["com.samsung.health.heart_rate.create_time"], errors="coerce")
        df = df.rename(columns={
            "com.samsung.health.heart_rate.heart_rate": "heart_rate"
        })
        df = df.dropna(subset=["time", "heart_rate"])
        df = df.sort_values(by="time")
        return df
    except Exception as e:
        print(f"Error loading heart rate data: {e}")
        return pd.DataFrame()


def load_stress_data(path="data/samsung health stress data.csv"):
    try:
        df = pd.read_csv(path)
        df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
        df = df[~df["score"].isna()]  # Drop rows with missing stress scores
        df = df.sort_values(by="start_time")
        return df
    except Exception as e:
        print(f"Error loading stress data: {e}")
        return pd.DataFrame()
