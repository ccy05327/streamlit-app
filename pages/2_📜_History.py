# pages/2_📜_History.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from utils import load
from utils.data_io import DATA_PATH

tz = ZoneInfo("Asia/Taipei")             # ensure consistency
st.title("📜 History  &  2025 Gap Filler")

# ------------------------------------------------------------------ #
# 1. Load all records → newest first                                  #
# ------------------------------------------------------------------ #
df_all = (
    load()
    .sort_values("start_time", ascending=False)
    .reset_index(drop=True)
)

# ------------------------------------------------------------------ #
# 2. PART A – EDITABLE view (2025 calendar)                           #
# ------------------------------------------------------------------ #
st.subheader("✏️ 2025 entries — fill in the blanks!")

# 2.1 Descending calendar (today ↓ 2025-01-01)
today = pd.Timestamp.now(tz).normalize()
start_date = pd.Timestamp("2025-01-01", tz=tz)
calendar = pd.DataFrame(
    {"date_only": pd.date_range(start_date, today, freq="D")}
).sort_values("date_only", ascending=False)

# 2.2 Merge existing 2025 rows
df_2025 = df_all[df_all["start_time"].dt.year == 2025].copy()
df_2025["date_only"] = df_2025["start_time"].dt.normalize()
calendar["date_only"] = calendar["date_only"].dt.tz_localize(None)
df_2025["date_only"] = df_2025["date_only"].dt.tz_localize(None)

merge_cols = [
    "start_time", "end_time",
    "physical_recovery", "mental_recovery",
    "sleep_cycle", "sleep_score", "sleep_duration"
]
df_2025_first = (
    df_2025.sort_values("start_time")
           .drop_duplicates("date_only", keep="first")
)
calendar = calendar.merge(
    df_2025_first[["date_only"] + merge_cols],
    on="date_only", how="left"
)

# 2.3 Build editor (start/end as HH:MM strings)
editor_df = calendar.copy()
editor_df["start_time"] = editor_df["start_time"].dt.strftime(
    "%H:%M").fillna("")
editor_df["end_time"] = editor_df["end_time"].dt.strftime("%H:%M").fillna("")
edited = st.data_editor(
    editor_df,
    num_rows="fixed",
    key="editor_2025",
    use_container_width=True,
    column_config={
        "date_only":      st.column_config.DatetimeColumn(format="YYYY-MM-DD", step=86400000),
        "sleep_duration": st.column_config.NumberColumn(format="%.2f"),
    },
)

# 2.4 Save-button block (unchanged)  ────────────────────────────────
# … keep your full save-button code here …
# ------------------------------------------------------------------ #

# ------------------------------------------------------------------ #
# 3. PART B – Read-only quick view                                    #
# ------------------------------------------------------------------ #
st.divider()
st.subheader("All records (newest → oldest)")
st.dataframe(
    df_all,
    use_container_width=True,
    hide_index=True,
    column_config={
        "sleep_duration": st.column_config.NumberColumn(format='%.2f')},
)
