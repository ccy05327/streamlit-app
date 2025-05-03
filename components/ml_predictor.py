# components/ml_predictor.py
import pandas as pd
from datetime import timedelta
from zoneinfo import ZoneInfo
from sklearn.neighbors import KNeighborsRegressor
from utils.data_io import load

tz = ZoneInfo("Asia/Taipei")


def _clean_df():
    """Return DF without NaNs in start_time, sorted chronologically."""
    df = load()
    df = df.dropna(subset=["start_time"]).copy()
    df["start_time"] = pd.to_datetime(df["start_time"])
    df.sort_values("start_time", inplace=True)
    return df


def _knn_model(k=3):
    df = _clean_df()
    if len(df) < k + 1:
        return None, df
    minutes = df["start_time"].dt.hour * 60 + df["start_time"].dt.minute
    X, y = minutes[:-1].values.reshape(-1, 1), minutes[1:]
    model = KNeighborsRegressor(n_neighbors=k).fit(X, y)
    return model, df


def _roll_one_step(model, last_start):
    last_min = last_start.hour * 60 + last_start.minute
    next_min = int(model.predict([[last_min]])[0]) % (24 * 60)
    h, m = divmod(next_min, 60)
    next_start = last_start.normalize().replace(hour=h, minute=m)
    if next_start <= last_start:
        next_start += timedelta(days=1)
    return next_start


def next_sleep_forecast():
    model, df = _knn_model()
    if model is None:
        return {"error": "Need more non-empty rows first."}

    last_start = df["start_time"].iloc[-1]
    next_start = _roll_one_step(model, last_start)
    duration = df["sleep_duration"].median()
    wake = next_start + timedelta(hours=duration)

    return {
        "date": next_start.date(),
        "sleep": next_start.strftime("%H:%M"),
        "wake":  wake.strftime("%H:%M"),
        "duration": round(duration, 2),
    }


def forecast_for_date(target_date):
    model, df = _knn_model()
    if model is None:
        return {"error": "Need more non-empty rows first."}

    cur = df["start_time"].iloc[-1]
    while cur.date() < target_date:
        cur = _roll_one_step(model, cur)
    duration = df["sleep_duration"].median()
    wake = cur + timedelta(hours=duration)
    return {
        "date": cur.date(),
        "sleep": cur.strftime("%H:%M"),
        "wake":  wake.strftime("%H:%M"),
        "duration": round(duration, 2),
    }
