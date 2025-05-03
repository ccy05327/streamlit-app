import sys
import pandas as pd
from datetime import datetime, timedelta


def fix_dates(input_path, output_path):
    """
    Reads a CSV with columns:
      date_only, start_time, end_time, physical_recovery, mental_recovery,
      sleep_cycle, sleep_score, sleep_duration

    Adjusts each 'start_time' and 'end_time' so their date matches 'date_only',
    handles overnight spans (end <= start → +1 day),
    recalculates 'sleep_duration' in hours (rounded to 2 decimals),
    and writes the corrected DataFrame (including duplicates) out to output_path.
    """
    # Load data, parsing original start/end (to capture time component)
    df = pd.read_csv(
        input_path,
        parse_dates=['start_time', 'end_time'],
        infer_datetime_format=True,
        low_memory=False
    )

    # Ensure 'date_only' is interpreted as a date
    df['date_only'] = pd.to_datetime(df['date_only'], errors='coerce').dt.date

    # Extract time-of-day from possibly misdated datetimes
    df['start_t'] = df['start_time'].dt.time
    df['end_t'] = df['end_time'].dt.time

    new_starts = []
    new_ends = []
    new_durs = []

    for _, row in df.iterrows():
        date = row['date_only']
        s_time = row['start_t']
        e_time = row['end_t']

        # If any key component is missing, leave as NaT/NA
        if pd.isna(date) or pd.isna(s_time) or pd.isna(e_time):
            new_starts.append(pd.NaT)
            new_ends.append(pd.NaT)
            new_durs.append(row.get('sleep_duration', pd.NA))
            continue

        # Combine date + time
        start_dt = datetime.combine(date, s_time)
        end_dt = datetime.combine(date, e_time)

        # Overnight: if end is on or before start, roll to next day
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        # Compute duration in hours, 2-decimal
        duration_h = round((end_dt - start_dt).total_seconds() / 3600.0, 2)

        new_starts.append(start_dt)
        new_ends.append(end_dt)
        new_durs.append(duration_h)

    # Assign corrected columns
    df['start_time'] = new_starts
    df['end_time'] = new_ends
    df['sleep_duration'] = new_durs

    # Drop temp columns
    df.drop(columns=['start_t', 'end_t'], inplace=True)

    # Reorder to your desired schema
    out_cols = [
        'date_only', 'start_time', 'end_time',
        'physical_recovery', 'mental_recovery',
        'sleep_cycle', 'sleep_score', 'sleep_duration'
    ]
    df = df[out_cols]

    # Write to CSV
    df.to_csv(output_path, index=False)
    print(f"Fixed dates & durations saved to: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python fix_dates.py input.csv output.csv')
        sys.exit(1)
    fix_dates(sys.argv[1], sys.argv[2])
