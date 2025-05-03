# pages/1_📥_Input.py
import streamlit as st
from utils import import_external, append
from components.sleep_form import sleep_entry_form
from utils.auth import check_password       # <- use new helper

st.title("📥 Input")

# ---------- File upload (viewable by anyone) -------------------------------
up = st.file_uploader("Import sleep CSV / JSON", type=["csv", "json"])
if up and check_password("input-import", prompt="Password to import"):
    new_rows = import_external(up)
    append(new_rows)
    st.success(f"Imported {len(new_rows)} rows from {up.name}")

st.divider()

# ---------- Manual entry ----------------------------------------------------
# sleep_entry_form will call check_password() ONLY when user clicks Save.
sleep_entry_form()
