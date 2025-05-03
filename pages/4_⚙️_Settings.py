# pages/4_⚙️_Settings.py
from utils.data_io import load
import pathlib
import os
import io
import pandas as pd
import streamlit as st
from utils.data_io import DATA_PATH, load, append
from utils.auth import check_password
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Settings")

tz = ZoneInfo("Asia/Taipei")

# ------------------------------------------------------------------ #
# 1. Data overview                                                   #
# ------------------------------------------------------------------ #
st.header("🗄️  Data overview")

if DATA_PATH.exists():
    df = load()
    rows = len(df)
    file_sz = DATA_PATH.stat().st_size / 1024
    st.write(
        f"**File:** `{DATA_PATH}`  |  **Rows:** {rows}  |  **Size:** {file_sz:.1f} kB")
else:
    st.warning(
        "`sleep_log.csv` not found – a new one will be created on first save.")
    df = pd.DataFrame()

st.divider()

# ------------------------------------------------------------------ #
# 2. Download backup                                                 #
# ------------------------------------------------------------------ #
st.subheader("📥  Download backup")

# 1) Load existing data (tz-naïve local times)
df = load()

# 2) Define a naïve start & end
START = pd.Timestamp("2025-01-01")                       # naïve
END = pd.Timestamp.now(ZoneInfo("Asia/Taipei"))        # tz-aware
END = END.normalize().tz_localize(None)                # strip tz → naïve

# 3) Build full calendar
dates = pd.date_range(START, END, freq="D")
calendar = pd.DataFrame({"date_only": dates})

# 4) Pull in your existing first-per-day rows
df_exist = df.copy()
df_exist["date_only"] = df_exist["start_time"].dt.normalize()
keep = ["date_only", "start_time", "end_time",
        "physical_recovery", "mental_recovery",
        "sleep_cycle", "sleep_score", "sleep_duration"]
df_exist = (
    df_exist
    .sort_values("start_time")
    .drop_duplicates("date_only", keep="first")
    [keep]
)

# 5) Merge so gaps stay blank
template = calendar.merge(df_exist, on="date_only", how="left")

# 6) Format times as HH:MM strings
for c in ("start_time", "end_time"):
    template[c] = template[c].dt.strftime("%H:%M").fillna("")

# 7) Offer for download
csv = template.to_csv(index=False)
st.download_button(
    "⬇️ Download 2025-template for Sheets",
    csv,
    file_name="sleep_2025_template.csv",
    mime="text/csv",
)

# ------------------------------------------------------------------ #
# 3. Upload / merge backup (password-gated)                          #
# ------------------------------------------------------------------ #
st.subheader("📤  Upload & merge")
up_file = st.file_uploader("Choose a CSV previously exported by this app",
                           type=["csv"])

if up_file:
    if check_password("settings-upload", prompt="🔒 Password to import"):
        try:
            new_df = pd.read_csv(up_file)
            append(new_df)
            st.success(f"Merged {len(new_df)} additional rows.")
            st.rerun()
        except Exception as e:
            st.error(f"Import failed: {e}")

st.divider()

# ------------------------------------------------------------------ #
# 4. Danger zone – clear ALL data                                    #
# ------------------------------------------------------------------ #
st.subheader("💥  Danger zone")
st.markdown(
    ":warning: **Delete ALL records** – this cannot be undone "
    "(unless you kept a backup above)."
)

if st.button("Delete sleep_log.csv"):
    if check_password("settings-clear", prompt="🔒 Confirm password to delete"):
        try:
            DATA_PATH.unlink(missing_ok=True)
            st.success(
                "File deleted. A fresh log will be created on next save.")
            st.rerun()
        except Exception as e:
            st.error(f"Delete failed: {e}")
