import pandas as pd
from utils import load
from sklearn.neighbors import KNeighborsRegressor


def next_sleep_forecast(k: int = 3) -> dict:
    df = load()
    if len(df) < k + 2:
        return {"error": "Need more data — log a few nights first."}

    # minutes since midnight → easier regression target
    t = pd.to_datetime(df["start_time"])
    minutes = t.dt.hour * 60 + t.dt.minute

    X = minutes[:-1].values.reshape(-1, 1)  # all but last
    y = minutes[1:]                         # next start times

    model = KNeighborsRegressor(n_neighbors=k)
    model.fit(X, y)

    next_minutes = int(model.predict([[minutes.iloc[-1]]])[0]) % (24*60)
    h, m = divmod(next_minutes, 60)
    next_time = f"{h:02d}:{m:02d}"

    # naïve duration = median of previous durations
    duration = df["sleep_duration"].median()
    end_minutes = (next_minutes + int(duration * 60)) % (24*60)
    eh, em = divmod(end_minutes, 60)
    wake_time = f"{eh:02d}:{em:02d}"

    return {"sleep": next_time, "wake": wake_time, "duration": round(duration, 2)}
