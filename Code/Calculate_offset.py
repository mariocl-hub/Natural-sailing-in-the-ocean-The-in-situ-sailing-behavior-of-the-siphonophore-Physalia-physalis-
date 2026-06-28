"""
Calculate_offset.py
-------------------
Estimates the temporal offset between buoy sensor timestamps (Y2K epoch stored
in the UTC column) and the UTC times embedded in the drone video filenames.

The script tries all possible differences (video_time - sensor_UTC) over a
sample of sensor rows, finds the most frequent value, and then counts how many
sensor records fall within ±2 min of each video clip. Corrected CSVs are saved
for manual inspection.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# --- CONFIGURATION ---
# Update these paths to match your local setup
WIND_CSV  = r"data/Sensor/Sensor_DataFiles/ulpgc-wind-buoy/20250730T070512_ulpgc-wind-buoy.csv"
DRIFT_CSV = r"data/Sensor/Sensor_DataFiles/ulpgc-drifter-buoy/20250730T070914_ulpgc-drifter-buoy.csv"

# UTC datetimes extracted from the video filenames (ISO 8601, UTC)
VIDEO_TIMES = {
    "DJI_20250730102351_0001_D_detected_cropped.mp4": "2025-07-30T10:23:51.379Z",
    "DJI_20250730102740_0002_D_detected_cropped.mp4": "2025-07-30T10:27:40.351Z",
    "DJI_20250730103129_0003_D_detected_cropped.mp4": "2025-07-30T10:31:29.168Z",
    "DJI_20250730103517_0004_D_detected_cropped.mp4": "2025-07-30T10:35:17.977Z",
}


def load_sensor_utc(path):
    df  = pd.read_csv(path)
    utc = pd.to_numeric(df["UTC"], errors="coerce").dropna().astype(int).values
    return df, utc


def compute_candidate_offsets(sensor_utcs, video_times_seconds, top_n=5):
    """
    Brute-force candidate offsets: video_time - sensor_UTC.
    We only sample the first 1000 sensor rows to keep it fast.
    """
    sensor_sample = sensor_utcs[:1000]
    diffs = []
    for s in sensor_sample:
        diffs.extend(list(video_times_seconds - s))
    diffs = np.array(diffs, dtype=np.int64)

    vals, counts = np.unique(diffs, return_counts=True)
    order = np.argsort(-counts)
    return list(zip(vals[order][:top_n].tolist(), counts[order][:top_n].tolist()))


def apply_offset_and_count(sensor_df, offset_seconds, video_times, pre_min=2, post_min=2):
    df = sensor_df.copy()
    df["UTC_num"]            = pd.to_numeric(df["UTC"], errors="coerce")
    df["datetime_corrected"] = pd.to_datetime(
        df["UTC_num"] + offset_seconds, unit="s", utc=True, errors="coerce"
    )
    counts = {}
    for vname, vtime in video_times.items():
        start         = vtime - pd.Timedelta(minutes=pre_min)
        end           = vtime + pd.Timedelta(minutes=post_min)
        mask          = (df["datetime_corrected"] >= start) & (df["datetime_corrected"] <= end)
        counts[vname] = int(mask.sum())
    return df, counts


def main():
    wind_df,  wind_utcs  = load_sensor_utc(WIND_CSV)
    drift_df, drift_utcs = load_sensor_utc(DRIFT_CSV)

    video_items = {name: pd.to_datetime(t, utc=True) for name, t in VIDEO_TIMES.items()}
    video_secs  = np.array([int(dt.timestamp()) for dt in video_items.values()])

    print("Computing candidate offsets (video_time - sensor_UTC)...")
    wind_top  = compute_candidate_offsets(wind_utcs,  video_secs, top_n=8)
    drift_top = compute_candidate_offsets(drift_utcs, video_secs, top_n=8)
    print(f"  Top candidates (wind):  {wind_top}")
    print(f"  Top candidates (drift): {drift_top}")

    # Prefer an offset that appears in both sensors; fall back to top drift candidate
    wind_candidates  = [t[0] for t in wind_top]
    drift_candidates = [t[0] for t in drift_top]
    common = [c for c in wind_candidates if c in drift_candidates]

    if common:
        chosen_offset = common[0]
        print(f"\nCommon offset found: {chosen_offset} s")
    else:
        chosen_offset = drift_candidates[0]
        print(f"\nNo common offset; using top drift candidate: {chosen_offset} s")

    wind_corrected,  wind_counts  = apply_offset_and_count(wind_df,  chosen_offset, video_items)
    drift_corrected, drift_counts = apply_offset_and_count(drift_df, chosen_offset, video_items)

    print("\nRecords per video ±2 min (wind):")
    for k, v in wind_counts.items():
        print(f"  {k}: {v}")

    print("\nRecords per video ±2 min (drift):")
    for k, v in drift_counts.items():
        print(f"  {k}: {v}")

    outdir = Path("offset_check_output")
    outdir.mkdir(exist_ok=True)
    wind_corrected.to_csv(outdir / "wind_with_corrected_datetime.csv",  index=False)
    drift_corrected.to_csv(outdir / "drift_with_corrected_datetime.csv", index=False)
    print(f"\nCorrected CSVs saved to: {outdir.resolve()}")
    print(f"Chosen offset: {chosen_offset} s  ({pd.Timedelta(seconds=int(chosen_offset))})")


if __name__ == "__main__":
    main()
