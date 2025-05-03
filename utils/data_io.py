from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd

TZ = ZoneInfo("Asia/Taipei")                # local zone
DATA_DIR = Path("data")
DATA_PATH = DATA_DIR / "sleep_log.csv"
SAMSUNG_CSV = DATA_DIR / "samsung_health_sleep_combined_data.csv"

COLUMNS = [
    "start_time", "end_time",
    "physical_recovery", "mental_recovery",
    "sleep_cycle", "sleep_score",
    "sleep_duration", "create_time", "update_time"
]

# ---------- helpers --------------------------------------------------------


def _localise(df: pd.DataFrame, cols) -> pd.DataFrame:
    """Assign Asia/Taipei tz to NAÏVE timestamps, then strip tz."""
    for c in cols:
        if c in df.columns:
            df[c] = (
                pd.to_datetime(df[c], errors="coerce")
                .dt.tz_localize(TZ, nonexistent="shift_forward", ambiguous="NaT")
                .dt.tz_localize(None)
            )
    return df

# 🔹 NEW – convert naïve-UTC → Asia/Taipei (then strip tz) ------------------


def _utc_to_local(df: pd.DataFrame, cols) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = (
                pd.to_datetime(df[c], errors="coerce")
                .dt.tz_localize("UTC")         # treat as UTC
                .dt.tz_convert(TZ)             # to GMT+8
                .dt.tz_localize(None)          # strip tz
            )
    return df


def _normalise_duration(df):  # (unchanged)
    if "sleep_duration" in df.columns:
        mask = df["sleep_duration"] > 24
        df.loc[mask, "sleep_duration"] = df.loc[mask, "sleep_duration"] / 60.0
    return df

# ---------- public API -----------------------------------------------------


def load() -> pd.DataFrame:
    DATA_DIR.mkdir(exist_ok=True)
    parse_cols = ["start_time", "end_time", "create_time", "update_time"]

    if DATA_PATH.exists() and DATA_PATH.stat().st_size:
        df = pd.read_csv(DATA_PATH, parse_dates=parse_cols)
        # app data already local
        return _localise(_normalise_duration(df), parse_cols)

    # 🔹 Samsung fallback — interpret times as **UTC** then shift +8
    if SAMSUNG_CSV.exists():
        # no update_time yet
        df = pd.read_csv(SAMSUNG_CSV, parse_dates=parse_cols[:-1])
        df = _utc_to_local(df, ["start_time", "end_time"])
        # the Samsung create_time is local
        df = _localise(df, ["create_time"])
        return _normalise_duration(df)

    return pd.DataFrame(columns=COLUMNS)


def append(df_new: pd.DataFrame) -> None:
    DATA_DIR.mkdir(exist_ok=True)

    # guarantee column presence / order
    for col in COLUMNS:
        if col not in df_new.columns:
            df_new[col] = pd.NA
    df_new = df_new[COLUMNS]

    df_all = pd.concat([load(), df_new], ignore_index=True)

    # 🔹 NEW — force datetime dtype so sort never mixes str vs Timestamp
    for col in ("start_time", "end_time", "create_time", "update_time"):
        df_all[col] = pd.to_datetime(df_all[col], errors="coerce")

    df_all.sort_values("start_time").to_csv(DATA_PATH, index=False)


def import_external(uploaded_file):  # (unchanged)
    if uploaded_file.type == "application/json" or uploaded_file.name.endswith(".json"):
        tmp = pd.read_json(uploaded_file)
    else:
        tmp = pd.read_csv(uploaded_file)

    tmp.columns = tmp.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)
    if "create_time" not in tmp.columns:
        tmp["create_time"] = pd.Timestamp.now(TZ).tz_localize(None)

    tmp = _normalise_duration(tmp)
    tmp = _localise(tmp, ["start_time", "end_time",
                    "create_time", "update_time"])
    return tmp[[c for c in COLUMNS if c in tmp.columns]]
