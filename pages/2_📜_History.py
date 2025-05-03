# pages/2_📜_History.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from utils.data_io import DATA_PATH, load
from utils.auth import check_password

tz = ZoneInfo("Asia/Taipei")
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
# 2. PART A – Editable gap-filler (2025 calendar)                     #
# ------------------------------------------------------------------ #
st.subheader("✏️ 2025 entries — fill the blanks!")

auth_edit = check_password("edit-history", prompt="Password to edit")

# 2.1 Descending calendar (today ↓ 2025-01-01) ----------------------
today = pd.Timestamp.now(tz).normalize()
start_date = pd.Timestamp("2025-01-01", tz=tz)
calendar = pd.DataFrame(
    {"date_only": pd.date_range(start_date, today, freq="D")}
).sort_values("date_only", ascending=False)

# 2.2 Merge existing rows (unchanged) -------------------------------
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
    df_2025_first[["date_only"] + merge_cols], on="date_only", how="left"
)

# 2.3 Editor dataframe ---------------------------------------------
editor_df = calendar.copy()
editor_df["start_time"] = editor_df["start_time"].dt.strftime(
    "%H:%M").fillna("")
editor_df["end_time"] = editor_df["end_time"].dt.strftime("%H:%M").fillna("")

edited = st.data_editor(
    editor_df,
    num_rows="fixed",
    key="editor_2025",
    use_container_width=True,
    disabled=not auth_edit,          # <- greyed-out until authorised
    column_config={
        "date_only":      st.column_config.DatetimeColumn(format="YYYY-MM-DD", step=86400000),
        "sleep_duration": st.column_config.NumberColumn(format="%.2f"),
    },
)

# 2.4 Save button – only works if authed ----------------------------
if st.button("💾 Save changes (2025)"):
    if not auth_edit:
        st.warning("Enter the password above before saving edits.")
        st.stop()

    # -------- SAVE-LOGIC START -------------------------------------------
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("Asia/Taipei")

    def _naive(dt):
        return dt.replace(tzinfo=None) if isinstance(dt, datetime) else dt

    now_local = _naive(datetime.now(tz))
    changed_rows, new_rows = 0, []

    for _, row in edited.iterrows():

        # skip completely blank calendar rows
        if not any([row["start_time"], row["end_time"],
                    row["physical_recovery"], row["mental_recovery"],
                    row["sleep_cycle"], row["sleep_score"]]):
            continue

        date = row["date_only"].date()
        st_str = row["start_time"]
        en_str = row["end_time"]

        st_dt = (datetime.combine(date, datetime.strptime(st_str, "%H:%M").time(), tz)
                 if st_str else None)
        en_dt = (datetime.combine(date, datetime.strptime(en_str, "%H:%M").time(), tz)
                 if en_str else None)

        if st_dt and en_dt and st_dt > en_dt:      # crosses midnight
            st_dt -= timedelta(days=1)

        duration_h = (round((en_dt - st_dt).total_seconds() / 3600, 2)
                      if st_dt and en_dt else pd.NA)

        # ------------------------------------------------------------------
        # 1️⃣  Does this exact (start,end) combo already exist?
        # ------------------------------------------------------------------
        mask = (df_all["start_time"] == _naive(st_dt)) & \
               (df_all["end_time"] == _naive(en_dt))

        if mask.any():            # -------- UPDATE -----------
            # -------- UPDATE (row exists) --------
            idx = mask.idxmax()
            prev = df_all.loc[idx]

            updated = {  # candidate new values
                "physical_recovery": row.get("physical_recovery"),
                "mental_recovery":   row.get("mental_recovery"),
                "sleep_cycle":       row.get("sleep_cycle"),
                "sleep_score":       row.get("sleep_score"),
                "sleep_duration":    duration_h if pd.notna(duration_h) else prev["sleep_duration"],
            }

            row_changed = False

            for col, val in updated.items():
                if pd.notna(val) and prev[col] != val:
                    df_all.at[idx, col] = val
                    row_changed = True

            if row_changed:                    # only then bump the timestamp
                df_all.at[idx, "update_time"] = now_local
                changed_rows += 1

        else:                      # -------- INSERT ----------
            new_rows.append({
                "start_time":        _naive(st_dt) if st_dt else pd.NaT,
                "end_time":          _naive(en_dt) if en_dt else pd.NaT,
                "physical_recovery": row.get("physical_recovery"),
                "mental_recovery":   row.get("mental_recovery"),
                "sleep_cycle":       row.get("sleep_cycle"),
                "sleep_score":       row.get("sleep_score"),
                "sleep_duration":    duration_h,
                "create_time":       now_local,
                "update_time":       now_local,
            })

    # ------------------------------------------------------------------
    # 2️⃣  Write back if anything changed                                #
    # ------------------------------------------------------------------
    if changed_rows or new_rows:
        if new_rows:
            df_all = pd.concat([df_all, pd.DataFrame(new_rows)],
                               ignore_index=True)

        for col in ("start_time", "end_time",
                    "create_time", "update_time"):
            df_all[col] = pd.to_datetime(df_all[col], errors="coerce")

        df_all.sort_values("start_time").to_csv(DATA_PATH, index=False)
        st.success(
            f"Saved {len(new_rows)} new row(s); updated {changed_rows} row(s).")
        (st.rerun if hasattr(st, "rerun") else st.experimental_rerun)()
    else:
        st.info("No changes detected.")
    # -------- SAVE-LOGIC END ---------------------------------------------

    st.success("Saved changes!")
    (st.rerun if hasattr(st, "rerun") else st.experimental_rerun)()

# ------------------------------------------------------------------ #

# ------------------------------------------------------------------ #
# 3. PART B – Read-only quick view                                   #
# ------------------------------------------------------------------ #
st.divider()
st.subheader("All records (newest → oldest)")
st.dataframe(
    df_all,
    use_container_width=True,
    hide_index=True,
    column_config={
        "sleep_duration": st.column_config.NumberColumn(format="%.2f")},
)
