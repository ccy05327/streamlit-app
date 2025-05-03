# pages/1_📥_Input.py
import streamlit as st
from utils import import_external, append
from components.sleep_form import sleep_entry_form
from utils.auth import check_password

st.title("📥 Input")

up = st.file_uploader(
    "Upload cleaned CSV (date_only, start_time, end_time, …)", type="csv"
)
if up:
    # ➊ Ask for password immediately on upload
    if not check_password("import-cleaned", prompt="🔒 Password to import"):
        st.stop()

    # ➋ Parse and write
    df_new = import_external(up)

    # ➌ Debug output: inspect what got parsed
    st.subheader("Parsed upload preview")
    st.dataframe(df_new.head(10))

    # ➍ Confirm success
    st.success(f"Imported {len(df_new)} rows into sleep_log.csv")


st.divider()

# ---------- Manual entry ----------------------------------------------------
# sleep_entry_form will call check_password() ONLY when user clicks Save.
sleep_entry_form()
