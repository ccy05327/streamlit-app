from pathlib import Path
import pandas as pd

DATA_PATH = Path("data") / "sleep_log.csv"
COLUMNS = [
    "start_time", "end_time",
    "physical_recovery", "mental_recovery",
    "sleep_cycle", "sleep_score",
    "sleep_duration", "create_time",
]


def load() -> pd.DataFrame:
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH, parse_dates=["start_time", "end_time", "create_time"])
    return pd.DataFrame(columns=COLUMNS)


def append(df_new: pd.DataFrame) -> None:
    df = load()
    df_all = pd.concat([df, df_new], ignore_index=True)
    df_all.to_csv(DATA_PATH, index=False)


def import_external(file) -> pd.DataFrame:
    """Accepts an uploaded CSV or JSON and normalises columns if possible."""
    if file.type == "application/json" or file.name.endswith(".json"):
        tmp = pd.read_json(file)
    else:
        tmp = pd.read_csv(file)
    # minimal normalisation – rename columns that match
    tmp = (
        tmp.rename(
            columns=lambda c: c.strip().lower().replace(" ", "_")
        )
        .assign(create_time=pd.Timestamp.utcnow())
    )
    cols_ok = [c for c in COLUMNS if c in tmp.columns]
    return tmp[cols_ok]
