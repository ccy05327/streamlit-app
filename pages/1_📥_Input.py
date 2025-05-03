import streamlit as st
from utils import import_external, append
from components.sleep_form import sleep_entry_form

st.title("📥 Input")

# --- File upload ----------------------------------------------------------
up = st.file_uploader("Import sleep CSV / JSON", type=["csv", "json"])
if up:
    new_rows = import_external(up)
    append(new_rows)
    st.success(f"Imported {len(new_rows)} rows from {up.name}")

st.divider()

# --- Manual entry ---------------------------------------------------------
sleep_entry_form()
