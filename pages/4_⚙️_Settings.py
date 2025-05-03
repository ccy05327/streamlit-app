# pages/4_⚙️_Settings.py
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
if df.empty:
    st.info("No rows to download yet.")
else:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    st.download_button("Download sleep_log.csv", buf.getvalue(),
                       file_name="sleep_log.csv", mime="text/csv")

st.divider()

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
