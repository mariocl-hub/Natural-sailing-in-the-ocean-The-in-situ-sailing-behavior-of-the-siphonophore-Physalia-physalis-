"""
Vectors_overlay_with_bins_v2_automatic.py
------------------------------------------
Batch version of Vectors_overlay_with_bins_v2.py.
Iterates over all clips in VIDEO_CONFIGS and writes one output video per clip.
The Bourg direction overlay is intentionally disabled in this version
(kept as a comment block for reference).
"""

import cv2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import os

# --- CONFIGURATION ---
DATA_FILE  = r"data/Sensor/Sensor_DataFiles/Global.xlsx"
DATA_ROOT  = r"data/Asturias_analized"

VIDEO_CONFIGS = {
    # ===== VIDEO 1 - 30_07_2025_10AM =====
    "video1_clip1": {
        "input":  f"{DATA_ROOT}/Video 1 (30_07_2025_10AM)/DJI_20250730102351_0001_D/DJI_20250730102351_0001_D_detected_cropped.mp4",
        "output": f"{DATA_ROOT}/Video 1 (30_07_2025_10AM)/DJI_20250730102351_0001_D/DJI_20250730102351_0001_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807186231,
    },
    "video1_clip2": {
        "input":  f"{DATA_ROOT}/Video 1 (30_07_2025_10AM)/DJI_20250730102351_0002_D/DJI_20250730102740_0002_D_detected_cropped.mp4",
        "output": f"{DATA_ROOT}/Video 1 (30_07_2025_10AM)/DJI_20250730102351_0002_D/DJI_20250730102740_0002_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807186460,
    },
    "video1_clip3": {
        "input":  f"{DATA_ROOT}/Video 1 (30_07_2025_10AM)/DJI_20250730102351_0003_D/DJI_20250730103129_0003_D_detected_cropped.mp4",
        "output": f"{DATA_ROOT}/Video 1 (30_07_2025_10AM)/DJI_20250730102351_0003_D/DJI_20250730103129_0003_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807186689,
    },
    "video1_clip4": {
        "input":  f"{DATA_ROOT}/Video 1 (30_07_2025_10AM)/DJI_20250730102351_0004_D/DJI_20250730103517_0004_D_detected_cropped.mp4",
        "output": f"{DATA_ROOT}/Video 1 (30_07_2025_10AM)/DJI_20250730102351_0004_D/DJI_20250730103517_0004_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807186918,
    },
    # ===== VIDEO 2 - 30_07_2025_11AM =====
    "video2_clip1": {
        "input":  f"{DATA_ROOT}/Video 2 (30_07_2025_11AM)/DJI_20250730110740_0003_D/DJI_20250730110740_0003_D_detected_cropped.MP4",
        "output": f"{DATA_ROOT}/Video 2 (30_07_2025_11AM)/DJI_20250730110740_0003_D/DJI_20250730110740_0003_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807188860,
    },
    "video2_clip2": {
        "input":  f"{DATA_ROOT}/Video 2 (30_07_2025_11AM)/DJI_20250730111129_0004_D/DJI_20250730111129_0004_D_detected_cropped.MP4",
        "output": f"{DATA_ROOT}/Video 2 (30_07_2025_11AM)/DJI_20250730111129_0004_D/DJI_20250730111129_0004_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807189089,
    },
    "video2_clip3": {
        "input":  f"{DATA_ROOT}/Video 2 (30_07_2025_11AM)/DJI_20250730111517_0005_D/DJI_20250730111517_0005_D_detected_cropped.mp4",
        "output": f"{DATA_ROOT}/Video 2 (30_07_2025_11AM)/DJI_20250730111517_0005_D/DJI_20250730111517_0005_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807189317,
    },
    "video2_clip4": {
        "input":  f"{DATA_ROOT}/Video 2 (30_07_2025_11AM)/DJI_20250730111906_0006_D/DJI_20250730111906_0006_D_detected_cropped.mp4",
        "output": f"{DATA_ROOT}/Video 2 (30_07_2025_11AM)/DJI_20250730111906_0006_D/DJI_20250730111906_0006_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807189546,
    },
    "video2_clip5": {
        "input":  f"{DATA_ROOT}/Video 2 (30_07_2025_11AM)/DJI_20250730112255_0007_D/DJI_20250730112255_0007_D_detected_cropped.mp4",
        "output": f"{DATA_ROOT}/Video 2 (30_07_2025_11AM)/DJI_20250730112255_0007_D/DJI_20250730112255_0007_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807189775,
    },
    # ===== VIDEO 3 - 30_07_2025_11_30AM =====
    "video3_clip1": {
        "input":  f"{DATA_ROOT}/Video 3 (30_07_2025_11_30AM)/DJI_20250730113843_0001_D/DJI_20250730113843_0001_D-002_detected_cropped.MP4",
        "output": f"{DATA_ROOT}/Video 3 (30_07_2025_11_30AM)/DJI_20250730113843_0001_D/DJI_20250730113843_0001_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807190723,
    },
    "video3_clip2": {
        "input":  f"{DATA_ROOT}/Video 3 (30_07_2025_11_30AM)/DJI_20250730114231_0002_D/DJI_20250730114231_0002_D-001_detected_cropped.MP4",
        "output": f"{DATA_ROOT}/Video 3 (30_07_2025_11_30AM)/DJI_20250730114231_0002_D/DJI_20250730114231_0002_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807190952,
    },
    "video3_clip3": {
        "input":  f"{DATA_ROOT}/Video 3 (30_07_2025_11_30AM)/DJI_20250730114620_0003_D/DJI_20250730114620_0003_D-003_detected_cropped.MP4",
        "output": f"{DATA_ROOT}/Video 3 (30_07_2025_11_30AM)/DJI_20250730114620_0003_D/DJI_20250730114620_0003_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807191180,
    },
    "video3_clip4": {
        "input":  f"{DATA_ROOT}/Video 3 (30_07_2025_11_30AM)/DJI_20250730115009_0004_D/DJI_20250730115009_0004_D-004_detected_cropped.MP4",
        "output": f"{DATA_ROOT}/Video 3 (30_07_2025_11_30AM)/DJI_20250730115009_0004_D/DJI_20250730115009_0004_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807191409,
    },
    "video3_clip5": {
        "input":  f"{DATA_ROOT}/Video 3 (30_07_2025_11_30AM)/DJI_20250730115358_0005_D/DJI_20250730115358_0005_D-005_detected_cropped.MP4",
        "output": f"{DATA_ROOT}/Video 3 (30_07_2025_11_30AM)/DJI_20250730115358_0005_D/DJI_20250730115358_0005_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807191638,
    },
}

# --- SHARED PARAMETERS ---
BIN_SECONDS           = 5
MAX_SPEED             = 10.0
APPLY_WIND_CORRECTION = True
WIND_DISPLAY_MODE     = "corrected"  # "both", "raw", or "corrected"
WIND_MIN_VALID        = 0
FPS_OVERRIDE          = None

CENTER       = (320, 320)
SCALE        = 25
THICKNESS    = 3
CENTER_COLOR = (255, 255, 255)

COLORS = {
    "wind":                (0, 255, 0),
    "current":             (255, 0, 0),
    "drone":               (0, 0, 255),
    "Expected trajectory": (255, 255, 0),
}

# --- HELPERS ---
def filter_by_speed(df_local, u_col, v_col, vmax):
    speed = np.hypot(df_local[u_col], df_local[v_col])
    df_local.loc[speed > vmax, [u_col, v_col]] = np.nan

def draw_solid_arrow(frame, start, end, color, thickness=2, tip_length=0.2):
    cv2.arrowedLine(frame, start, end, color, thickness, tipLength=tip_length)

def draw_vector_at_center(frame, u, v, color, scale=1.0):
    if u is None or v is None or np.isnan(u) or np.isnan(v):
        return np.nan
    dx    = u * scale
    dy    = v * scale
    start = (int(round(CENTER[0])),      int(round(CENTER[1])))
    end   = (int(round(CENTER[0] + dx)), int(round(CENTER[1] - dy)))
    draw_solid_arrow(frame, start, end, color, thickness=THICKNESS)
    return np.hypot(u, v)

def put_text_with_bg(frame, text, org, font=cv2.FONT_HERSHEY_SIMPLEX,
                     font_scale=0.45, text_color=(0, 0, 0),
                     bg_color=(255, 255, 255), thickness=1, padding=4):
    """Draw text with a filled background rectangle for readability."""
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    x, y         = org
    top_left     = (x - padding,          y - text_h - padding)
    bottom_right = (x + text_w + padding, y + baseline + padding)
    cv2.rectangle(frame, top_left, bottom_right, bg_color, -1)
    cv2.putText(frame, text, org, font, font_scale, text_color, thickness, cv2.LINE_AA)


def process_clip(name, config):
    VIDEO_IN          = config["input"]
    VIDEO_OUT         = config["output"]
    VIDEO_START_EPOCH = config["epoch"]

    # Load and sort sensor data
    if DATA_FILE.lower().endswith(".csv"):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.read_excel(DATA_FILE)

    df = df.sort_values("UTC (Y2K epoch)").reset_index(drop=True)
    df["datetime UTC (+2)"] = df["datetime UTC (+2)"].astype(str)

    required_cols = [
        "UTC (Y2K epoch)",
        "u_wind_raw", "v_wind_raw",
        "Sensor_u_drift", "Sensor_v_drift",
        "u_current", "v_current",
        "u_drone", "v_drone",
        "Lat_drone", "Lon_drone",
    ]
    for c in required_cols:
        if c not in df.columns:
            raise ValueError(f"Missing column: {c}")

    for col in ["u_wind_raw", "v_wind_raw", "Sensor_u_drift", "Sensor_v_drift",
                "u_current", "v_current", "u_drone", "v_drone",
                "Lat_drone", "Lon_drone"]:
        df[col] = (
            df[col].astype(str)
            .str.replace(",", ".", regex=False)
            .replace(to_replace=r"[^\d\.\-]+", value=np.nan, regex=True)
            .astype(float)
        )

    epochs = df["UTC (Y2K epoch)"].values

    filter_by_speed(df, "u_wind_raw",       "v_wind_raw",       MAX_SPEED)
    filter_by_speed(df, "u_wind_corrected", "v_wind_corrected", MAX_SPEED)
    filter_by_speed(df, "u_current",        "v_current",        MAX_SPEED)
    filter_by_speed(df, "u_drone",          "v_drone",          MAX_SPEED)

    df["wind_speed_raw"]       = np.hypot(df["u_wind_raw"],       df["v_wind_raw"])
    df["wind_speed_corrected"] = np.hypot(df["u_wind_corrected"], df["v_wind_corrected"])
    df["current_speed"]        = np.hypot(df["u_current"],        df["v_current"])
    df["drone_speed"]          = np.hypot(df["u_drone"],          df["v_drone"])

    # Wind speed at 10 m (log-profile extrapolation from 0.525 m sensor height)
    wind_speeds_ref = np.array([1, 2, 4, 6, 7, 8, 10, 12])
    z0_ref          = np.array([4.71, 6.60, 27.2, 38.3, 43.3, 48.3, 72.1, 95.9]) * 1e-5

    def get_z0(ws):
        return z0_ref[np.abs(wind_speeds_ref - ws).argmin()]

    df["z0"]             = [get_z0(ws) for ws in df["wind_speed_corrected"]]
    df["wind_speed_10m"] = df["wind_speed_corrected"] * (
        np.log(10 / df["z0"]) / np.log(0.525 / df["z0"])
    )

    # Bourg expected drift angle: Alpha = 50.8 * exp(-0.15 * U10) - 0.5
    df["expected_trajectory"] = 50.8 * np.exp(-0.15 * df["wind_speed_10m"]) - 0.5

    t0             = epochs.min()
    df["time_bin"] = ((df["UTC (Y2K epoch)"] - t0) // BIN_SECONDS).astype(int)

    bin_means = (
        df.groupby("time_bin")
        .agg(
            u_wind_raw           = ("u_wind_raw",           "mean"),
            v_wind_raw           = ("v_wind_raw",           "mean"),
            wind_speed_raw       = ("wind_speed_raw",       "mean"),
            u_wind_corrected     = ("u_wind_corrected",     "mean"),
            v_wind_corrected     = ("v_wind_corrected",     "mean"),
            wind_speed_corrected = ("wind_speed_corrected", "mean"),
            u_current            = ("u_current",            "mean"),
            v_current            = ("v_current",            "mean"),
            current_speed        = ("current_speed",        "mean"),
            u_drone              = ("u_drone",              "mean"),
            v_drone              = ("v_drone",              "mean"),
            drone_speed          = ("drone_speed",          "mean"),
            datetime             = ("datetime UTC (+2)",    "first"),
            epoch_mean           = ("UTC (Y2K epoch)",      "mean"),
            bourg_direction      = ("expected_trajectory",  "mean"),
        )
        .reset_index()
    )

    total_bins = int(bin_means["time_bin"].nunique())

    cap = cv2.VideoCapture(VIDEO_IN)
    if not cap.isOpened():
        raise IOError(f"Could not open video: {VIDEO_IN}")

    fps    = FPS_OVERRIDE or cap.get(cv2.CAP_PROP_FPS)
    w      = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out    = cv2.VideoWriter(VIDEO_OUT, fourcc, fps, (w, h))

    mode_txt = (
        "MODE: BOTH (corrected solid / raw dashed)" if WIND_DISPLAY_MODE == "both"
        else ("MODE: RAW (raw dashed only)"          if WIND_DISPLAY_MODE == "raw"
              else "MODE: CORRECTED (corrected solid only)")
    )

    frame_idx        = 0
    DRONE_VISUAL_SCALE = 20.0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_epoch = VIDEO_START_EPOCH + frame_idx / fps
        bin_idx     = int((frame_epoch - t0) // BIN_SECONDS)
        row_bin     = bin_means[bin_means["time_bin"] == bin_idx]

        if row_bin.empty:
            cv2.putText(frame, mode_txt,                   (10, h - 55), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            cv2.putText(frame, f"Total bins: {total_bins}",(10, h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            cv2.putText(frame, f"Bin idx: {bin_idx}",      (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            out.write(frame)
            frame_idx += 1
            continue

        row = row_bin.iloc[0]
        cv2.circle(frame, CENTER, 4, CENTER_COLOR, -1)

        # Wind vector (negated to show going-to direction)
        mag_corr    = draw_vector_at_center(frame, -row.u_wind_corrected, -row.v_wind_corrected, COLORS["wind"],    SCALE)
        mag_current = draw_vector_at_center(frame,  row.u_current,         row.v_current,         COLORS["current"], SCALE)
        mag_drone   = draw_vector_at_center(frame,  row.u_drone,           row.v_drone,           COLORS["drone"],   SCALE * DRONE_VISUAL_SCALE)

        # Bourg direction overlay is disabled; uncomment to re-enable
        # if not pd.isna(row.bourg_direction):
        #     draw_bourg_direction(frame, row.bourg_direction, COLORS["Expected trajectory"])

        cv2.putText(frame, f"UTC epoch: {frame_epoch:.2f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, "Date/time (UTC+2):",            (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)
        cv2.putText(frame, str(row["datetime"]),             (10, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

        y0 = 75
        dy = 18

        if not pd.isna(row.wind_speed_corrected):
            net_corr = mag_corr if not np.isnan(mag_corr) else np.nan
            put_text_with_bg(frame, f"Wind CORR: {row.wind_speed_corrected:.2f} m/s | net {net_corr:.2f}",
                             (10, y0), text_color=COLORS["wind"])
        else:
            msg = (f"Wind CORR: not observable (apparent < {WIND_MIN_VALID} m/s)"
                   if APPLY_WIND_CORRECTION else "Wind CORR: correction disabled")
            put_text_with_bg(frame, msg, (10, y0), text_color=(150, 150, 150))
        y0 += dy

        if not pd.isna(row.current_speed):
            net = mag_current if not np.isnan(mag_current) else np.nan
            put_text_with_bg(frame, f"Current: {row.current_speed:.2f} m/s | net {net:.2f}",
                             (10, y0), text_color=COLORS["current"])
            y0 += dy

        if not pd.isna(row.drone_speed):
            net = mag_drone if not np.isnan(mag_drone) else np.nan
            put_text_with_bg(frame, f"Drone: {row.drone_speed:.2f} m/s | net {net:.2f}",
                             (10, y0), text_color=COLORS["drone"])
            y0 += dy

        cv2.putText(frame, f"Temporal averaging: {BIN_SECONDS} s (binning)",
                    (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
    print(f"  Saved: {VIDEO_OUT}")


# --- RUN ---
for name, config in VIDEO_CONFIGS.items():
    print(f"\nProcessing {name}...")
    process_clip(name, config)
