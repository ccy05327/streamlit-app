import json
import pandas as pd
from datetime import datetime, timedelta


def load_sleep_data(filepath):
    with open(filepath, "r") as f:
        raw_data = json.load(f)

    records = []
    for entry in raw_data["sleep_record"]:
        date = entry["date"]
        sleep = entry["sleep"]
        wake = entry["wake"]

        sleep_time = datetime(int(date["year"]), int(date["month"]), int(date["day"]),
                              int(sleep["hour"]), int(sleep["min"]))
        wake_time = datetime(int(date["year"]), int(date["month"]), int(date["day"]),
                             int(wake["hour"]), int(wake["min"]))
        if wake_time <= sleep_time:
            wake_time += timedelta(days=1)

        records.append({
            "sleep_time": sleep_time,
            "wake_time": wake_time,
            "duration": entry.get("duration", round((wake_time - sleep_time).seconds / 3600, 2)),
            "mood": None  # You can update this later
        })

    return pd.DataFrame(records)
