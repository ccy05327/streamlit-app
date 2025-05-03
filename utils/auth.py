# utils/auth.py
import streamlit as st
from hashlib import sha256

HASH = st.secrets["PWD_HASH"]


def _hash_ok(pwd: str) -> bool:
    return sha256(pwd.encode()).hexdigest() == HASH


def check_password(action: str,
                   prompt: str = "🔒 Password",
                   button: str = "OK") -> bool:
    """
    Returns True once per session/tab for `action`.
    Accepts <Enter> in the input OR the button click.
    """
    flag = f"auth_{action}"
    if st.session_state.get(flag):
        return True

    # Wrap the input in a form so hitting <Enter> submits
    with st.form(f"pwd_form_{action}", clear_on_submit=True):
        pwd = st.text_input(prompt, type="password")
        submitted = st.form_submit_button(button)

    if submitted:
        if _hash_ok(pwd):
            st.session_state[flag] = True
            (st.rerun if hasattr(st, "rerun") else st.experimental_rerun)()
        else:
            st.error("❌ Incorrect password")
    return False
