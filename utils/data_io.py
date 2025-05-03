# utils/data_io.py
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd
from datetime import datetime, timedelta

# ── Constants & paths ─────────────────────────────────────────────────────
TZ = ZoneInfo("Asia/Taipei")                  # local zone
DATA_DIR = Path("data")
DATA_PATH = DATA_DIR / "sleep_log.csv"
SAMSUNG_CSV = DATA_DIR / "samsung_health_sleep_combined_data.csv"
CLEANED_CSV = Path("cleaned_sleep_data_2025.csv")      # your filled template

COLUMNS = [
    "start_time", "end_time",
    "physical_recovery", "mental_recovery",
    "sleep_cycle", "sleep_score",
    "sleep_duration", "create_time", "update_time"
]

# ── Helpers ────────────────────────────────────────────────────────────────


def _localise(df: pd.DataFrame, cols) -> pd.DataFrame:
    """Assign Asia/Taipei tz to naïve timestamps, then strip tz."""
    for c in cols:
        if c in df.columns:
            df[c] = (
                pd.to_datetime(df[c], errors="coerce")
                .dt.tz_localize(TZ, nonexistent="shift_forward", ambiguous="NaT")
                .dt.tz_localize(None)
            )
    return df


def _utc_to_local(df: pd.DataFrame, cols) -> pd.DataFrame:
    """Convert naïve UTC timestamps → Asia/Taipei, then strip tz."""
    for c in cols:
        if c in df.columns:
            df[c] = (
                pd.to_datetime(df[c], errors="coerce")
                .dt.tz_localize("UTC")
                .dt.tz_convert(TZ)
                .dt.tz_localize(None)
            )
    return df


def _normalise_duration(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Samsung’s minutes (>24) into hours.float everywhere."""
    if "sleep_duration" in df.columns:
        mask = df["sleep_duration"] > 24
        df.loc[mask, "sleep_duration"] = df.loc[mask, "sleep_duration"] / 60.0
    return df

# ── Public API ────────────────────────────────────────────────────────────


def load() -> pd.DataFrame:
    """
    Load the primary data source:
    1) If cleaned_sleep_data_2025.csv exists, load & return that.
    2) Else if sleep_log.csv exists (and non-empty), load & return it.
    3) Else if Samsung CSV exists, load that (converting from UTC to local).
    4) Otherwise return an empty DataFrame.
    """
    DATA_DIR.mkdir(exist_ok=True)
    parse_cols = ["start_time", "end_time", "create_time", "update_time"]

    # 1) Your cleaned, complete data takes precedence
    if CLEANED_CSV.exists():
        df = pd.read_csv(
            CLEANED_CSV,
            parse_dates=parse_cols,
            infer_datetime_format=True,
            low_memory=False,)
        return _localise(_normalise_duration(df), parse_cols)

    # 2) User-generated log
    if DATA_PATH.exists() and DATA_PATH.stat().st_size:
        df = pd.read_csv(DATA_PATH, parse_dates=parse_cols)
        return _localise(_normalise_duration(df), parse_cols)

    # 3) Samsung fallback (assume UTC timestamps)
    if SAMSUNG_CSV.exists():
        df = pd.read_csv(SAMSUNG_CSV, parse_dates=parse_cols[:-1])
        df = _utc_to_local(df, ["start_time", "end_time"])
        return _localise(_normalise_duration(df), ["create_time"])

    # 4) Empty slate
    return pd.DataFrame(columns=COLUMNS)


def append(df_new: pd.DataFrame) -> None:
    """
    Append new rows to sleep_log.csv (creating it if needed).
    """
    DATA_DIR.mkdir(exist_ok=True)

    # Ensure all columns exist in the correct order
    for col in COLUMNS:
        if col not in df_new.columns:
            df_new[col] = pd.NA
    df_new = df_new[COLUMNS]

    df_all = pd.concat([load(), df_new], ignore_index=True)

    # Force datetime dtype so sorting never mixes strings & Timestamps
    for col in ("start_time", "end_time", "create_time", "update_time"):
        df_all[col] = pd.to_datetime(df_all[col], errors="coerce")

    df_all.sort_values("start_time").to_csv(DATA_PATH, index=False)


def import_external(uploaded_file) -> pd.DataFrame:
    """
    Read a cleaned CSV with:
      date_only, start_time, end_time,
      physical_recovery, mental_recovery,
      sleep_cycle, sleep_score, sleep_duration

    • Keeps duplicate dates
    • Parses full datetimes or HH:MM + date_only
    • Handles cross-midnight sleeps
    • Leaves existing sleep_duration, fills only missing
    • Stamps create/update time and writes data/sleep_log.csv
    """
    # 1️⃣ Load raw CSV into DataFrame
    tmp = pd.read_csv(uploaded_file)

    # 2️⃣ Normalize column names
    tmp.columns = tmp.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)

    # 3️⃣ Parse date_only to a date
    tmp["date_only"] = pd.to_datetime(
        tmp["date_only"], errors="coerce").dt.date

    # 4️⃣ Smart parser: try full datetime, else HH:MM + date_only
    def parse_dt(val, date_only):
        if pd.notna(val):
            # 4.a) Try ISO datetime first
            dt = pd.to_datetime(val, errors="coerce")
            if pd.notna(dt):
                return dt.to_pydatetime()
            # 4.b) Fallback to HH:MM next to a date_only
            s = str(val).strip()
            if date_only and s:
                try:
                    t = datetime.strptime(s, "%H:%M").time()
                    return datetime.combine(date_only, t)
                except ValueError:
                    return pd.NaT
        return pd.NaT

    tmp["start_time"] = tmp.apply(lambda r: parse_dt(
        r.get("start_time"), r["date_only"]), axis=1)
    tmp["end_time"] = tmp.apply(lambda r: parse_dt(
        r.get("end_time"),   r["date_only"]), axis=1)

    # 5️⃣ Handle cross-midnight (if end < start → +1 day)
    tmp["end_time"] = tmp.apply(
        lambda r: (r["end_time"] + timedelta(days=1))
        if pd.notna(r["start_time"]) and pd.notna(r["end_time"]) and r["end_time"] < r["start_time"]
        else r["end_time"],
        axis=1
    )

    # 6️⃣ Calculate any missing durations (hours, 2 decimals)
    def calc_dur(r):
        if pd.notna(r.get("sleep_duration")):
            return r["sleep_duration"]
        s, e = r["start_time"], r["end_time"]
        if pd.isna(s) or pd.isna(e):
            return pd.NA
        return round((e - s).total_seconds() / 3600.0, 2)

    tmp["sleep_duration"] = tmp.apply(calc_dur, axis=1)

    # 7️⃣ Stamp create_time & update_time
    now = pd.Timestamp.now(TZ).tz_localize(None)
    tmp["create_time"] = now
    tmp["update_time"] = now

    # 8️⃣ Reorder & write out
    out = tmp[[
        "start_time", "end_time",
        "physical_recovery", "mental_recovery",
        "sleep_cycle", "sleep_score",
        "sleep_duration", "create_time", "update_time"
    ]].copy()

    # Ensure data dir & write
    DATA_DIR.mkdir(exist_ok=True)
    out.sort_values("start_time")\
       .to_csv(DATA_DIR / "sleep_log.csv", index=False)

    return out
