# Guarda esto como "compute_and_check_offset.py" y ejecútalo.
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta

# Rutas (ajusta si hace falta)
WIND_CSV = r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Sensor\Sensor_DataFiles\ulpgc-wind-buoy\20250730T070512_ulpgc-wind-buoy.csv"
DRIFT_CSV = r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Sensor\Sensor_DataFiles\ulpgc-drifter-buoy\20250730T070914_ulpgc-drifter-buoy.csv"

# Video JSON: copia exactamente el bloque que me enviaste (o pon la ruta al JSON)
video_json = {
  "C:/Users/Usuario/Documents/Mario/Estudios/Master Universitario/TFM/database/DJI_20250730102351_0001_D/DJI_20250730102351_0001_D_detected_cropped.mp4": "2025-07-30T10:23:51.379Z",
  "C:/Users/Usuario/Documents/Mario/Estudios/Master Universitario/TFM/database/DJI_20250730102351_0002_D/DJI_20250730102740_0002_D_detected_cropped.mp4": "2025-07-30T10:27:40.351Z",
  "C:/Users/Usuario/Documents/Mario/Estudios/Master Universitario/TFM/database/DJI_20250730102351_0003_D/DJI_20250730103129_0003_D_detected_cropped.mp4": "2025-07-30T10:31:29.168Z",
  "C:/Users/Usuario/Documents/Mario/Estudios/Master Universitario/TFM/database/DJI_20250730102351_0004_D/DJI_20250730103517_0004_D_detected_cropped.mp4": "2025-07-30T10:35:17.977Z"
}

def load_sensor_utc(path):
    df = pd.read_csv(path)
    utc = pd.to_numeric(df['UTC'], errors='coerce').dropna().astype(int).values
    return df, utc

def compute_candidate_offsets(sensor_utcs, video_times_seconds, top_n=5):
    # compute all differences video_time - sensor_utc for samples (limit for speed)
    sensor_sample = sensor_utcs[:1000]
    diffs = []
    for s in sensor_sample:
        diffs.extend(list(video_times_seconds - s))
    diffs = np.array(diffs, dtype=np.int64)
    # round and count most common
    vals, counts = np.unique(diffs, return_counts=True)
    order = np.argsort(-counts)
    top = list(zip(vals[order][:top_n].tolist(), counts[order][:top_n].tolist()))
    return top

def apply_offset_and_count(sensor_df, offset_seconds, video_times, pre_min=2, post_min=2):
    # assume naive mapping: real_time = offset + UTC_seconds
    df = sensor_df.copy()
    # create corrected datetime
    df['UTC_num'] = pd.to_numeric(df['UTC'], errors='coerce')
    df['datetime_corrected'] = pd.to_datetime(df['UTC_num'] + offset_seconds, unit='s', utc=True, errors='coerce')
    counts = {}
    for vname, vtime in video_times.items():
        start = vtime - pd.Timedelta(minutes=pre_min)
        end = vtime + pd.Timedelta(minutes=post_min)
        mask = (df['datetime_corrected'] >= start) & (df['datetime_corrected'] <= end)
        counts[vname] = int(mask.sum())
    return df, counts

def main():
    wind_df, wind_utcs = load_sensor_utc(WIND_CSV)
    drift_df, drift_utcs = load_sensor_utc(DRIFT_CSV)

    # prepare video times (seconds)
    video_items = [(Path(k).name, pd.to_datetime(v, utc=True)) for k,v in video_json.items()]
    video_times = {name: dt for name, dt in video_items}
    video_secs = np.array([int(dt.timestamp()) for _, dt in video_items])

    print("Computing candidate offsets (video_time - sensor_utc)...")
    wind_top = compute_candidate_offsets(wind_utcs, video_secs, top_n=8)
    drift_top = compute_candidate_offsets(drift_utcs, video_secs, top_n=8)
    print("Top candidate offsets (seconds) from wind:", wind_top)
    print("Top candidate offsets (seconds) from drift:", drift_top)

    # Take the top candidate that appears in both lists (if any), otherwise take top from drift
    wind_candidates = [t[0] for t in wind_top]
    drift_candidates = [t[0] for t in drift_top]
    common = [c for c in wind_candidates if c in drift_candidates]
    if common:
        chosen_offset = common[0]
        print("Found common offset:", chosen_offset)
    else:
        # fallback: choose top of drift (usually more reliable)
        chosen_offset = drift_candidates[0]
        print("No common offset; using top drift candidate:", chosen_offset)

    # Apply chosen_offset and count per video
    wind_corrected_df, wind_counts = apply_offset_and_count(wind_df, chosen_offset, video_times)
    drift_corrected_df, drift_counts = apply_offset_and_count(drift_df, chosen_offset, video_times)

    print("\nCounts per video after applying offset (wind):")
    for k,v in wind_counts.items():
        print(f"  {k}: {v} wind records in ±2 min")

    print("\nCounts per video after applying offset (drift):")
    for k,v in drift_counts.items():
        print(f"  {k}: {v} drift records in ±2 min")

    # save corrected CSVs for inspection
    outdir = Path("./offset_check_output")
    outdir.mkdir(exist_ok=True)
    wind_corrected_df.to_csv(outdir / "wind_with_corrected_datetime.csv", index=False)
    drift_corrected_df.to_csv(outdir / "drift_with_corrected_datetime.csv", index=False)
    print(f"\nSaved corrected CSVs in {outdir.resolve()}")

    # show the chosen offset in human-readable form
    offset_td = pd.Timedelta(seconds=int(chosen_offset))
    print("\nChosen offset (seconds):", chosen_offset)
    print("Chosen offset (timedelta):", offset_td)

if __name__ == '__main__':
    main()
