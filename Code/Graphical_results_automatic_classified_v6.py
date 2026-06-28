from datetime import timedelta, timezone
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, FancyArrowPatch
import matplotlib.patheffects as path_effects
from matplotlib.ticker import FuncFormatter
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import cv2

################
## DATA ENTRY ##
################
excel_file = r"D:\Mario\TFM\database\Sensor\Sensor_DataFiles\Global.xlsx"
sheet_name = 0

OUTPUT_DIR = r"D:\Mario\TFM\database\analysis\Graphical results of flights with nodes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

VIDEO_CLIPS = {
    "v1_complete": (807179031, 807179788),
    "v1_clip1": (807179031, 807179260),
    "v1_clip2": (807179260, 807179489),
    "v1_clip3": (807179489, 807179717),
    "v1_clip4": (807179717, 807179788),
    "v2_complete": (807181660, 807182709),
    "v2_clip1": (807181660, 807181889),
    "v2_clip2": (807181889, 807182117),
    "v2_clip3": (807182117, 807182346),
    "v2_clip4": (807182346, 807182575),
    "v2_clip5": (807182575, 807182709),
    "v3_complete": (807183523, 807184587),
    "v3_clip1": (807183523, 807183752),
    "v3_clip2": (807183752, 807183980),
    "v3_clip3": (807183980, 807184209),
    "v3_clip4": (807184209, 807184438),
    "v3_clip5": (807184438, 807184587),
    "v4_complete": (807184906, 807185592),
    "v4_clip1": (807184906, 807185135),
    "v4_clip2": (807185135, 807185364),
    "v4_clip3": (807185364, 807185592),
    "v5_complete": (807613096,807614128),
    "v5_clip1": (807613096,807613324),
    "v5_clip2": (807613324,807613553),
    "v5_clip3": (807613553,807613782),
    "v5_clip4": (807613782,807614011),
    "v5_clip5": (807614011,807614128),
    "v6_complete": (807614788,807615828),
    "v6_clip1": (807614788,807615027),
    "v6_clip2": (807615027,807615256),
    "v6_clip3": (807615256,807615485),
    "v6_clip4": (807615485,807615714),
    "v6_clip5": (807615714,807615828),
    "v7_complete": (807616389,807617440),
    "v7_clip1": (807616389,807616618),
    "v7_clip2": (807616618,807616847),
    "v7_clip3": (807616847,807617076),
    "v7_clip4": (807617076,807617304),
    "v7_clip5": (807617304,807617440),
    "v8_complete": (807618280,807618998),
    "v8_clip1": (807618280,807618508),
    "v8_clip2": (807618508,807618737),
    "v8_clip3": (807618737,807618966),
    "v8_clip4": (807618966,807618998),
}

CLIP_DELAYS = {
    "v1_complete": 36,
    "v1_clip1":    36,
    "v2_complete": 60,
    "v2_clip1":    60,
    "v3_complete": 0,
    "v3_clip1":    0,
    "v3_clip3":    60,
    "v4_complete": 11,
    "v4_clip1":    11,
    "v4_clip2":    0,
    "v4_clip3":    0,
}

COMPLETE_CLIP_SUBCLIPS = {
    "v1_complete": ["v1_clip1", "v1_clip2", "v1_clip3", "v1_clip4"],
    "v2_complete": ["v2_clip1", "v2_clip2", "v2_clip3", "v2_clip4", "v2_clip5"],
    "v3_complete": ["v3_clip1", "v3_clip2", "v3_clip3", "v3_clip4", "v3_clip5"],
    "v4_complete": ["v4_clip1", "v4_clip2", "v4_clip3", "v4_clip4"],
    "v5_complete": ["v5_clip1", "v5_clip2", "v5_clip3", "v5_clip4", "v5_clip5"],
    "v6_complete": ["v6_clip1", "v6_clip2", "v6_clip3", "v6_clip4", "v6_clip5"],
    "v7_complete": ["v7_clip1", "v7_clip2", "v7_clip3", "v7_clip4", "v7_clip5"],
    "v8_complete": ["v8_clip1", "v8_clip2", "v8_clip3", "v8_clip4"],
}

CLASSIFICATION_FILES = {
    "v1_clip1":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0001_D\DJI_20250730102351_0001_D_detected_cropped_classified.csv",
    "v1_clip2":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0002_D\DJI_20250730102740_0002_D_detected_cropped_classified.csv",
    "v1_clip3":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0003_D\DJI_20250730103129_0003_D_detected_cropped_classified.csv",
    "v1_clip4":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0004_D\DJI_20250730103517_0004_D_detected_cropped_classified.csv",
    "v2_clip1":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730110740_0003_D\DJI_20250730110740_0003_D_detected_cropped_classified.csv",
    "v2_clip2":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111129_0004_D\DJI_20250730111129_0004_D_detected_cropped_classified.csv",
    "v2_clip3":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111517_0005_D\DJI_20250730111517_0005_D_detected_cropped_classified.csv",
    "v2_clip4":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111906_0006_D\DJI_20250730111906_0006_D_detected_cropped_classified.csv",
    "v2_clip5":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730112255_0007_D\DJI_20250730112255_0007_D_detected_cropped_classified.csv",
    "v3_clip1":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730113843_0001_D\DJI_20250730113843_0001_D_detected_cropped_classified.csv",
    "v3_clip2":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730114231_0002_D\DJI_20250730114231_0002_D_detected_cropped_classified.csv",
    "v3_clip3":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730114620_0003_D\DJI_20250730114620_0003_D_detected_cropped_classified.csv",
    "v3_clip4":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730115009_0004_D\DJI_20250730115009_0004_D_detected_cropped_classified.csv",
    "v3_clip5":    r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730115358_0005_D\DJI_20250730115358_0005_D_detected_cropped_classified.csv",
}

VIDEO_FILES = {
    "v1_clip1": r"D:\Mario\TFM\database\Asturias\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0001_D\DJI_20250730102351_0001_D_detected_cropped.mp4",
    "v1_clip2": r"D:\Mario\TFM\database\Asturias\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0002_D\DJI_20250730102740_0002_D_detected_cropped.mp4",
    "v1_clip3": r"D:\Mario\TFM\database\Asturias\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0003_D\DJI_20250730103129_0003_D_detected_cropped.mp4",
    "v1_clip4": r"D:\Mario\TFM\database\Asturias\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0004_D\DJI_20250730103517_0004_D_detected_cropped.mp4",
    "v2_clip1": r"D:\Mario\TFM\database\Asturias\Video 2 (30_07_2025_11AM)\DJI_20250730110740_0003_D\DJI_20250730110740_0003_D_detected_cropped.MP4",
    "v2_clip2": r"D:\Mario\TFM\database\Asturias\Video 2 (30_07_2025_11AM)\DJI_20250730111129_0004_D\DJI_20250730111129_0004_D_detected_cropped.MP4",
    "v2_clip3": r"D:\Mario\TFM\database\Asturias\Video 2 (30_07_2025_11AM)\DJI_20250730111517_0005_D\DJI_20250730111517_0005_D_detected_cropped.MP4",
    "v2_clip4": r"D:\Mario\TFM\database\Asturias\Video 2 (30_07_2025_11AM)\DJI_20250730111906_0006_D\DJI_20250730111906_0006_D_detected_cropped.MP4",
    "v2_clip5": r"D:\Mario\TFM\database\Asturias\Video 2 (30_07_2025_11AM)\DJI_20250730112255_0007_D\DJI_20250730112255_0007_D_detected_cropped.MP4",
    "v3_clip1": r"D:\Mario\TFM\database\Asturias\Video 3 (30_07_2025_11_30AM)\DJI_20250730113843_0001_D\DJI_20250730113843_0001_D-002_detected_cropped.MP4",
    "v3_clip2": r"D:\Mario\TFM\database\Asturias\Video 3 (30_07_2025_11_30AM)\DJI_20250730114231_0002_D\DJI_20250730114231_0002_D-001_detected_cropped.MP4",
    "v3_clip3": r"D:\Mario\TFM\database\Asturias\Video 3 (30_07_2025_11_30AM)\DJI_20250730114620_0003_D\DJI_20250730114620_0003_D-003_detected_cropped.MP4",
    "v3_clip4": r"D:\Mario\TFM\database\Asturias\Video 3 (30_07_2025_11_30AM)\DJI_20250730115009_0004_D\DJI_20250730115009_0004_D-004_detected_cropped.MP4",
    "v3_clip5": r"D:\Mario\TFM\database\Asturias\Video 3 (30_07_2025_11_30AM)\DJI_20250730115358_0005_D\DJI_20250730115358_0005_D-005_detected_cropped.MP4",
    "v4_clip1": r"D:\Mario\TFM\database\Asturias\Video 4 (30_07_2025_12AM)\DJI_20250730120146_0001_D\DJI_20250730120146_0001_D_detected_cropped.MP4",
    "v4_clip2": r"D:\Mario\TFM\database\Asturias\Video 4 (30_07_2025_12AM)\DJI_20250730120535_0002_D\DJI_20250730120535_0002_D_detected_cropped.MP4",
    "v4_clip3": r"D:\Mario\TFM\database\Asturias\Video 4 (30_07_2025_12AM)\DJI_20250730120924_0003_D\DJI_20250730120924_0003_D_detected_cropped.MP4",
    "v5_clip1": r"D:\Mario\TFM\database\Asturias\Video 5 (20250730_BUCKET#019_drone-camera_DJI_202508041055_005)\DJI_20250804105815_0001_D\DJI_20250804105815_0001_D_detected_cropped.MP4",
    "v5_clip2": r"D:\Mario\TFM\database\Asturias\Video 5 (20250730_BUCKET#019_drone-camera_DJI_202508041055_005)\DJI_20250804110204_0002_D\DJI_20250804110204_0002_D_detected_cropped.MP4",
    "v5_clip3": r"D:\Mario\TFM\database\Asturias\Video 5 (20250730_BUCKET#019_drone-camera_DJI_202508041055_005)\DJI_20250804110553_0003_D\DJI_20250804110553_0003_D_detected_cropped.MP4",
    "v5_clip4": r"D:\Mario\TFM\database\Asturias\Video 5 (20250730_BUCKET#019_drone-camera_DJI_202508041055_005)\DJI_20250804110942_0004_D\DJI_20250804110942_0004_D_detected_cropped.MP4",
    "v5_clip5": r"D:\Mario\TFM\database\Asturias\Video 5 (20250730_BUCKET#019_drone-camera_DJI_202508041055_005)\DJI_20250804111331_0005_D\DJI_20250804111331_0005_D_detected_cropped.MP4",
    "v6_clip1": r"D:\Mario\TFM\database\Asturias\Video 6 (20250730_BUCKET#007_drone-camera_DJI_202508041123_006)\DJI_20250804112638_0001_D\DJI_20250804112638_0001_D_detected_cropped.MP4",
    "v6_clip2": r"D:\Mario\TFM\database\Asturias\Video 6 (20250730_BUCKET#007_drone-camera_DJI_202508041123_006)\DJI_20250804113027_0002_D\DJI_20250804113027_0002_D_detected_cropped.MP4",
    "v6_clip3": r"D:\Mario\TFM\database\Asturias\Video 6 (20250730_BUCKET#007_drone-camera_DJI_202508041123_006)\DJI_20250804113416_0003_D\DJI_20250804113416_0003_D_detected_cropped.MP4",
    "v6_clip4": r"D:\Mario\TFM\database\Asturias\Video 6 (20250730_BUCKET#007_drone-camera_DJI_202508041123_006)\DJI_20250804113805_0004_D\DJI_20250804113805_0004_D_detected_cropped.MP4",
    "v6_clip5": r"D:\Mario\TFM\database\Asturias\Video 6 (20250730_BUCKET#007_drone-camera_DJI_202508041123_006)\DJI_20250804114153_0005_D\DJI_20250804114153_0005_D_detected_cropped.MP4",
    "v7_clip1": r"D:\Mario\TFM\database\Asturias\Video 7 (20250730_BUCKET#008_drone-camera_DJI_202508041150_007)\DJI_20250804115309_0001_D\DJI_20250804115309_0001_D_detected_cropped.MP4",
    "v7_clip2": r"D:\Mario\TFM\database\Asturias\Video 7 (20250730_BUCKET#008_drone-camera_DJI_202508041150_007)\DJI_20250804115658_0002_D\DJI_20250804115658_0002_D_detected_cropped.MP4",
    "v7_clip3": r"D:\Mario\TFM\database\Asturias\Video 7 (20250730_BUCKET#008_drone-camera_DJI_202508041150_007)\DJI_20250804120047_0003_D\DJI_20250804120047_0003_D_detected_cropped.MP4",
    "v7_clip4": r"D:\Mario\TFM\database\Asturias\Video 7 (20250730_BUCKET#008_drone-camera_DJI_202508041150_007)\DJI_20250804120436_0004_D\DJI_20250804120436_0004_D_detected_cropped.MP4",
    "v7_clip5": r"D:\Mario\TFM\database\Asturias\Video 7 (20250730_BUCKET#008_drone-camera_DJI_202508041150_007)\DJI_20250804120824_0005_D\DJI_20250804120824_0005_D_detected_cropped.MP4",
    "v8_clip1": r"D:\Mario\TFM\database\Asturias\Video 8 (20250730_BUCKET#009_drone-camera_DJI_202508041221_008)\DJI_20250804122439_0001_D\DJI_20250804122439_0001_D_detected_cropped.MP4",
    "v8_clip2": r"D:\Mario\TFM\database\Asturias\Video 8 (20250730_BUCKET#009_drone-camera_DJI_202508041221_008)\DJI_20250804122828_0002_D\DJI_20250804122828_0002_D_detected_cropped.MP4",
    "v8_clip3": r"D:\Mario\TFM\database\Asturias\Video 8 (20250730_BUCKET#009_drone-camera_DJI_202508041221_008)\DJI_20250804123217_0003_D\DJI_20250804123217_0003_D_detected_cropped.MP4",
    "v8_clip4": r"D:\Mario\TFM\database\Asturias\Video 8 (20250730_BUCKET#009_drone-camera_DJI_202508041221_008)\DJI_20250804123217_0003_D\DJI_20250804123217_0003_D_detected_cropped.MP4",
}

###############
## CONSTANTS ##
###############
dt_interp = "1s"
node_step = 30
vector_scale = 0.1
spatial_margin = 0.000003
max_drone_speed = 1

wind_scale_factor = 4
current_scale_factor = 8

meters_per_degree_lon = 80668.3864
meters_per_degree_lat = 111320.0

lat_min, lat_max = 43.50, 43.60
lon_min, lon_max = -5.70, -5.55

THUMB_SIZE = (80, 45)

WIND_COLOR    = "#2ecc40"
CURRENT_COLOR = "#0074d9"

REFERENCE_SPEED = 1


#####################
## HELPER FUNCTIONS ##
#####################
def find_subclip_for_epoch(clip_name, node_epoch_y2k):
    subclips = COMPLETE_CLIP_SUBCLIPS.get(clip_name, [])
    for sc in subclips:
        sc_start, sc_end = VIDEO_CLIPS[sc]
        if sc_start <= node_epoch_y2k <= sc_end:
            return VIDEO_FILES.get(sc), sc_start
    return None, None


def extract_frame_at_epoch(video_path, node_epoch_y2k, clip_start_epoch_y2k,
                            thumb_size=THUMB_SIZE):
    if not video_path or not os.path.exists(video_path):
        print(f"  [WARNING] Video not found: {video_path}")
        return None
    offset_seconds = node_epoch_y2k - clip_start_epoch_y2k
    if offset_seconds < 0:
        print(f"  [WARNING] Invalid time offset for {video_path}")
        return None
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  [WARNING] Could not open video: {video_path}")
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        cap.release()
        return None
    target_frame = int(offset_seconds * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        print(f"  [WARNING] Could not read frame {target_frame} from {video_path}")
        return None
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return cv2.resize(frame_rgb, thumb_size, interpolation=cv2.INTER_AREA)


def plot_thumbnail_at_node(ax, img_array, lon, lat, zoom=0.5,
                            offset_points=(0, 70)):
    if img_array is None:
        return

    renderer     = ax.figure.canvas.get_renderer()
    ax_bbox      = ax.get_window_extent(renderer=renderer)
    node_disp    = ax.transData.transform((lon, lat))

    hw = int(THUMB_SIZE[0] * zoom * 0.75) + 6
    hh = int(THUMB_SIZE[1] * zoom * 0.75) + 6
    MARGIN = hw + 8

    cx = node_disp[0] + offset_points[0]
    cy = node_disp[1] + offset_points[1]

    clamped_cx = float(np.clip(cx, ax_bbox.x0 + MARGIN, ax_bbox.x1 - MARGIN))
    clamped_cy = float(np.clip(cy, ax_bbox.y0 + hh + 8, ax_bbox.y1 - hh - 8))

    thumb_data = ax.transData.inverted().transform((clamped_cx, clamped_cy))
    node_data  = (lon, lat)

    ax.plot(
        [node_data[0], thumb_data[0]],
        [node_data[1], thumb_data[1]],
        color='black', lw=0.8, zorder=4,
        solid_capstyle='round'
    )

    imagebox = OffsetImage(img_array, zoom=zoom)
    imagebox.image.axes = ax

    ab = AnnotationBbox(
        imagebox,
        xy=thumb_data,
        xycoords='data',
        xybox=(0, 0),
        boxcoords='offset points',
        pad=0.3,
        bboxprops=dict(boxstyle='round,pad=0.2', facecolor='white',
                       edgecolor='black', linewidth=0.8, alpha=0.9),
        arrowprops=None,
        zorder=7
    )
    ax.add_artist(ab)


def _segments_intersect(p1, p2, p3, p4):
    def cross2d(a, b):
        return a[0] * b[1] - a[1] * b[0]
    d1 = (p2[0] - p1[0], p2[1] - p1[1])
    d2 = (p4[0] - p3[0], p4[1] - p3[1])
    denom = cross2d(d1, d2)
    if abs(denom) < 1e-10:
        return False
    diff = (p3[0] - p1[0], p3[1] - p1[1])
    t = cross2d(diff, d2) / denom
    u = cross2d(diff, d1) / denom
    return 1e-6 < t < 1 - 1e-6 and 1e-6 < u < 1 - 1e-6


def _connector_crosses_existing(node_disp, thumb_center, existing_connectors):
    for (en, et) in existing_connectors:
        if _segments_intersect(node_disp, thumb_center, en, et):
            return True
    return False


def build_density_map(ax, fig, lon_d, lat_d, valid_mask,
                      uw_scaled, vw_scaled, uc_scaled, vc_scaled):
    renderer = fig.canvas.get_renderer()
    W = int(renderer.width)
    H = int(renderer.height)
    occupancy = np.zeros((H, W), dtype=bool)

    def _clip_px(v, lo, hi):
        return int(np.clip(v, lo, hi))

    def mark_line(x0, y0, x1, y1, thickness=6):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        steps = max(dx, dy, 1)
        for i in range(int(steps) + 1):
            t = i / steps
            px = int(x0 + t * (x1 - x0))
            py = int(y0 + t * (y1 - y0))
            row = H - 1 - py
            r0 = _clip_px(row - thickness, 0, H - 1)
            r1 = _clip_px(row + thickness, 0, H - 1)
            c0 = _clip_px(px  - thickness, 0, W - 1)
            c1 = _clip_px(px  + thickness, 0, W - 1)
            if r1 > r0 and c1 > c0:
                occupancy[r0:r1, c0:c1] = True

    def mark_circle(cx, cy, radius):
        r   = int(radius)
        row = H - 1 - int(cy)
        r0  = _clip_px(row - r, 0, H - 1)
        r1  = _clip_px(row + r, 0, H - 1)
        c0  = _clip_px(int(cx) - r, 0, W - 1)
        c1  = _clip_px(int(cx) + r, 0, W - 1)
        if r1 > r0 and c1 > c0:
            occupancy[r0:r1, c0:c1] = True

    valid_lons = lon_d[valid_mask]
    valid_lats = lat_d[valid_mask]
    if len(valid_lons) > 1:
        pts = ax.transData.transform(np.column_stack([valid_lons, valid_lats]))
        for i in range(len(pts) - 1):
            mark_line(pts[i, 0], pts[i, 1],
                      pts[i+1, 0], pts[i+1, 1], thickness=10)

    NODE_PAD   = 28
    VECTOR_PAD = 9

    for i in range(len(lon_d)):
        if np.isnan(lon_d[i]) or np.isnan(lat_d[i]):
            continue
        xn, yn = ax.transData.transform((lon_d[i], lat_d[i]))
        mark_circle(xn, yn, NODE_PAD)
        if not (np.isnan(uw_scaled[i]) or np.isnan(vw_scaled[i])):
            xt, yt = ax.transData.transform(
                (lon_d[i] + uw_scaled[i], lat_d[i] + vw_scaled[i]))
            mark_line(xn, yn, xt, yt, thickness=VECTOR_PAD)
            mark_circle(xt, yt, NODE_PAD // 2 + 4)
        if not (np.isnan(uc_scaled[i]) or np.isnan(vc_scaled[i])):
            xt, yt = ax.transData.transform(
                (lon_d[i] + uc_scaled[i], lat_d[i] + vc_scaled[i]))
            mark_line(xn, yn, xt, yt, thickness=VECTOR_PAD)
            mark_circle(xt, yt, NODE_PAD // 2 + 4)

    return occupancy


def find_best_offset(ax, fig, lon, lat, existing_boxes, thumb_zoom,
                     occupancy, existing_connectors, node_index=0):

    direction_groups = [
        [(0,   90), (0,  120), (0,  155), (0,  185), (0,  215)],
        [(0,  -90), (0, -120), (0, -155), (0, -185), (0, -215)],
        [(-90,  0), (-120, 0), (-155,  0), (-185, 0), (-215,  0)],
        [( 90,  0), ( 120, 0), ( 155,  0), ( 185, 0), ( 215,  0)],
    ]
    diagonals = [
        ( 70,  70), (-70,  70), ( 70, -70), (-70, -70),
        (105, 105), (-105, 105), (105, -105), (-105, -105),
        (140, 140), (-140, 140), (140, -140), (-140, -140),
        (175, 175), (-175, 175), (175, -175), (-175, -175),
        (210, 210), (-210, 210), (210, -210), (-210, -210),
    ]
    wide_fallbacks = [
        (0, 240), (0, -240), (240, 0), (-240, 0),
        (0, 270), (0, -270), (270, 0), (-270, 0),
        (0, 300), (0, -300), (300, 0), (-300, 0),
        (130, 200), (-130, 200), (130, -200), (-130, -200),
        (200, 130), (-200, 130), (200, -130), (-200, -130),
    ]
    ordered = (direction_groups[node_index % 4] +
               direction_groups[(node_index + 1) % 4] +
               direction_groups[(node_index + 2) % 4] +
               direction_groups[(node_index + 3) % 4] +
               diagonals +
               wide_fallbacks)

    renderer  = fig.canvas.get_renderer()
    H = int(renderer.height)
    W = int(renderer.width)

    hw = int(THUMB_SIZE[0] * thumb_zoom * 0.75)
    hh = int(THUMB_SIZE[1] * thumb_zoom * 0.75)

    node_disp = ax.transData.transform((lon, lat))
    ax_bbox   = ax.get_window_extent(renderer=renderer)

    MARGIN        = hw + 8
    CROSS_PENALTY = 3000

    best_offset = None
    best_score  = float('inf')

    for offset in ordered:
        cx = node_disp[0] + offset[0]
        cy = node_disp[1] + offset[1]

        thumb_left   = cx - hw
        thumb_right  = cx + hw
        thumb_bottom = cy - hh
        thumb_top    = cy + hh

        if (thumb_left  < ax_bbox.x0 + MARGIN or
                thumb_right  > ax_bbox.x1 - MARGIN or
                thumb_bottom < ax_bbox.y0 + MARGIN or
                thumb_top    > ax_bbox.y1 - MARGIN):
            bounds_penalty = 1e9
        else:
            bounds_penalty = 0

        occ_row_centre = H - 1 - int(cy)
        r0 = int(np.clip(occ_row_centre - hh, 0, H - 1))
        r1 = int(np.clip(occ_row_centre + hh, 0, H - 1))
        c0 = int(np.clip(int(cx) - hw,        0, W - 1))
        c1 = int(np.clip(int(cx) + hw,        0, W - 1))
        occ_score = (int(occupancy[r0:r1, c0:c1].sum()) * 3
                     if r1 > r0 and c1 > c0 else 0)

        thumb_overlap = sum(
            1 for (bx, by, bw, bh) in existing_boxes
            if abs(cx - bx) < (hw + bw) and abs(cy - by) < (hh + bh)
        ) * 1e9

        dist_penalty = (offset[0]**2 + offset[1]**2) ** 0.5 * 0.3

        thumb_center = (cx, cy)
        cross_count  = sum(
            1 for (en, et) in existing_connectors
            if _segments_intersect(node_disp, thumb_center, en, et)
        )
        cross_penalty = cross_count * CROSS_PENALTY

        score = bounds_penalty + thumb_overlap + occ_score + dist_penalty + cross_penalty

        if score < best_score:
            best_score  = score
            best_offset = offset

    if best_offset is None:
        best_offset = ordered[0]

    cx_f = node_disp[0] + best_offset[0]
    cy_f = node_disp[1] + best_offset[1]
    existing_boxes.append((cx_f, cy_f, hw, hh))
    existing_connectors.append((tuple(node_disp), (cx_f, cy_f)))

    occ_row_f = H - 1 - int(cy_f)
    r0p = int(np.clip(occ_row_f - hh, 0, H - 1))
    r1p = int(np.clip(occ_row_f + hh, 0, H - 1))
    c0p = int(np.clip(int(cx_f) - hw, 0, W - 1))
    c1p = int(np.clip(int(cx_f) + hw, 0, W - 1))
    if r1p > r0p and c1p > c0p:
        occupancy[r0p:r1p, c0p:c1p] = True

    return best_offset


def find_empty_corner(ax, lon_d, lat_d, valid_mask, exclude=None):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xmid = (xlim[0] + xlim[1]) / 2
    ymid = (ylim[0] + ylim[1]) / 2
    lons = lon_d[valid_mask]
    lats = lat_d[valid_mask]
    counts = {
        'upper right': np.sum((lons > xmid) & (lats > ymid)),
        'upper left':  np.sum((lons < xmid) & (lats > ymid)),
        'lower right': np.sum((lons > xmid) & (lats < ymid)),
        'lower left':  np.sum((lons < xmid) & (lats < ymid)),
    }
    if exclude:
        counts = {k: v for k, v in counts.items() if k not in exclude}
    return min(counts, key=counts.get)


def draw_vector_key(fig, ax, corner, ref_speed,
                    wind_scale_factor, current_scale_factor,
                    vector_scale, meters_per_degree_lon):
    ax_pos = ax.get_position()

    wind_len_deg    = (ref_speed / meters_per_degree_lon) * vector_scale * wind_scale_factor
    current_len_deg = (ref_speed / meters_per_degree_lon) * vector_scale * current_scale_factor
    max_len_deg     = max(wind_len_deg, current_len_deg)

    wind_ratio    = wind_len_deg    / max_len_deg
    current_ratio = current_len_deg / max_len_deg

    START_X        = 0.12
    MAX_ARROW_FRAC = 0.72
    END_X_MAX      = START_X + MAX_ARROW_FRAC

    wind_end_x    = START_X + MAX_ARROW_FRAC * wind_ratio
    current_end_x = START_X + MAX_ARROW_FRAC * current_ratio

    WIND_Y    = 0.72
    CURR_Y    = 0.28
    LABEL_OFF = 0.18

    wind_label    = f"Wind  {ref_speed:.0f} m/s"
    current_label = f"Current  {ref_speed:.0f} m/s"
    panel_w = 0.075
    panel_h = 0.072

    pad = 0.01
    if corner == 'upper right':
        x0 = ax_pos.x1 - panel_w - pad;  y0 = ax_pos.y1 - panel_h - pad
    elif corner == 'upper left':
        x0 = ax_pos.x0 + pad;            y0 = ax_pos.y1 - panel_h - pad
    elif corner == 'lower right':
        x0 = ax_pos.x1 - panel_w - pad;  y0 = ax_pos.y0 + pad
    else:
        x0 = ax_pos.x0 + pad;            y0 = ax_pos.y0 + pad

    inset = fig.add_axes([x0, y0, panel_w, panel_h])
    inset.set_xlim(0, 1)
    inset.set_ylim(0, 1)
    inset.set_xticks([])
    inset.set_yticks([])
    inset.patch.set_facecolor('white')
    inset.patch.set_alpha(0.85)
    for spine in inset.spines.values():
        spine.set_linewidth(0.8)

    inset.annotate(
        "", xy=(wind_end_x, WIND_Y), xytext=(START_X, WIND_Y),
        arrowprops=dict(arrowstyle="-|>", color=WIND_COLOR,
                        lw=1.8, mutation_scale=10),
        zorder=5
    )
    inset.text(
        START_X + (wind_end_x - START_X) / 2,
        WIND_Y + LABEL_OFF,
        wind_label,
        ha='center', va='center', fontsize=6.5,
        color=WIND_COLOR, fontweight='bold',
        clip_on=False
    )

    inset.annotate(
        "", xy=(current_end_x, CURR_Y), xytext=(START_X, CURR_Y),
        arrowprops=dict(arrowstyle="-|>", color=CURRENT_COLOR,
                        lw=1.8, mutation_scale=10),
        zorder=5
    )
    inset.text(
        START_X + (current_end_x - START_X) / 2,
        CURR_Y - LABEL_OFF,
        current_label,
        ha='center', va='center', fontsize=6.5,
        color=CURRENT_COLOR, fontweight='bold',
        clip_on=False
    )

    inset.set_zorder(20)

    fig_w_px, fig_h_px = fig.get_size_inches() * fig.dpi
    px_x0 = x0      * fig_w_px
    px_y0 = y0      * fig_h_px
    px_w  = panel_w * fig_w_px
    px_h  = panel_h * fig_h_px

    return inset, (px_x0, px_y0, px_w, px_h)


############################
## DATA LOAD AND CLEANING ##
############################
cols = [
    "UTC (Y2K epoch)",
    "Lat_wind", "Lon_wind", "u_wind_corrected", "v_wind_corrected",
    "Lat_current", "Lon_current", "u_current", "v_current",
    "Lat_drone", "Lon_drone", "u_drone", "v_drone"
]

base_df = pd.read_excel(excel_file, sheet_name=sheet_name)[cols]


def clean_numeric_series(series):
    if pd.api.types.is_numeric_dtype(series):
        return series
    s = series.astype(str).str.replace(',', '.').str.replace(
        r'[^\d\.\-]', '', regex=True)
    return pd.to_numeric(s, errors='coerce')


for col in base_df.columns:
    if col != "UTC (Y2K epoch)":
        base_df[col] = clean_numeric_series(base_df[col])


#######################################
## MAIN PROCESSING FUNCTION PER CLIP ##
#######################################
def process_clip(clip_name, START_EPOCH, END_EPOCH):
    print(f"\n=== Processing {clip_name} ===")
    data_frame = base_df.copy()

    data_frame["datetime"] = pd.to_datetime(
        data_frame["UTC (Y2K epoch)"], unit="s",
        origin=pd.Timestamp("2000-01-01")
    ).dt.tz_localize("UTC")

    df = data_frame.set_index("datetime").sort_index()

    delay = CLIP_DELAYS.get(clip_name, 0)
    t0 = pd.to_datetime(START_EPOCH + delay, unit="s",
                        origin=pd.Timestamp("2000-01-01")).tz_localize("UTC")
    t1 = pd.to_datetime(END_EPOCH, unit="s",
                        origin=pd.Timestamp("2000-01-01")).tz_localize("UTC")

    df = df.loc[t0:t1]
    if df.empty:
        print("No data in range. Skipping.")
        return

    full_index = pd.date_range(df.index.min(), df.index.max(), freq=dt_interp)
    df = df.reindex(full_index).interpolate()

    y2k_origin = pd.Timestamp("2000-01-01 00:00:00", tz="UTC")
    df["epoch_y2k"] = (df.index - y2k_origin).total_seconds()

    df["Lat_drone"] = df["Lat_drone"].round(8)
    df["Lon_drone"] = df["Lon_drone"].round(8)
    mask_geo = (
        (df["Lat_drone"] < lat_min - spatial_margin) |
        (df["Lat_drone"] > lat_max + spatial_margin) |
        (df["Lon_drone"] < lon_min - spatial_margin) |
        (df["Lon_drone"] > lon_max + spatial_margin)
    )
    df.loc[mask_geo, ["Lat_drone", "Lon_drone"]] = np.nan

    df["drone_speed"] = np.sqrt(df["u_drone"]**2 + df["v_drone"]**2)
    df.loc[df["drone_speed"] > max_drone_speed, ["u_drone", "v_drone"]] = np.nan

    valid_drone_times = df.dropna(subset=["Lat_drone", "Lon_drone"]).index
    node_times = valid_drone_times[::node_step]
    num_nodes  = len(node_times)
    print(f"Total number of nodes: {num_nodes}")

    node_epochs_y2k = df.loc[node_times, "epoch_y2k"].values

    class_file = CLASSIFICATION_FILES.get(clip_name)
    classification_df = pd.DataFrame(columns=['letter'])
    if class_file and os.path.exists(class_file):
        try:
            _df = pd.read_csv(class_file)
            if not _df.empty and 'class' in _df.columns:
                _df['letter'] = _df['class'].astype(str).str.split('_').str[0]
                classification_df = _df
            else:
                print(f"  [WARNING] Empty or missing 'class' column: {class_file}")
        except pd.errors.EmptyDataError:
            print(f"  [WARNING] Empty classification file: {class_file}")

    node_letters = [
        classification_df.loc[i, 'letter'] if i < len(classification_df) else ''
        for i in range(num_nodes)
    ]

    lat_d = df.loc[node_times, "Lat_drone"].values
    lon_d = df.loc[node_times, "Lon_drone"].values
    uw = df.loc[node_times, "u_wind_corrected"].values
    vw = df.loc[node_times, "v_wind_corrected"].values
    uc = df.loc[node_times, "u_current"].values
    vc = df.loc[node_times, "v_current"].values

    valid_mask = ~np.isnan(lat_d) & ~np.isnan(lon_d)

    mean_lat = np.nanmean(lat_d[valid_mask]) if np.any(valid_mask) else 43.5
    meters_per_degree_lon_local = 111320 * np.cos(np.radians(mean_lat))
    meters_per_degree_lat_local = 111320.0

    uw_scaled = (uw / meters_per_degree_lon_local) * vector_scale * wind_scale_factor
    vw_scaled = (vw / meters_per_degree_lat_local) * vector_scale * wind_scale_factor
    uc_scaled = (uc / meters_per_degree_lon_local) * vector_scale * current_scale_factor
    vc_scaled = (vc / meters_per_degree_lat_local) * vector_scale * current_scale_factor

    segment_speeds = []
    for i in range(len(node_times) - 1):
        t_start = node_times[i]
        t_end   = node_times[i + 1]
        seg_speeds = df.loc[t_start:t_end, "drone_speed"].dropna()
        seg_speeds = seg_speeds[seg_speeds <= 10]
        segment_speeds.append(seg_speeds.mean() if not seg_speeds.empty else np.nan)

    if num_nodes <= 8:
        thumb_zoom = 0.6
    elif num_nodes <= 14:
        thumb_zoom = 0.45
    else:
        thumb_zoom = 0.3
    print(f"Thumbnail zoom: {thumb_zoom} ({num_nodes} nodes)")

    video_path = VIDEO_FILES.get(clip_name)

    node_frames = []
    for i in range(num_nodes):
        ep = node_epochs_y2k[i]
        if video_path:
            frame = extract_frame_at_epoch(video_path, ep, START_EPOCH)
        else:
            sub_path, sub_start = find_subclip_for_epoch(clip_name, ep)
            frame = extract_frame_at_epoch(sub_path, ep, sub_start) if sub_path else None
        node_frames.append(frame)

    print(f"Frames extracted: {sum(f is not None for f in node_frames)}/{num_nodes}")

    #################
    ## MAIN FIGURE ##
    #################
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.subplots_adjust(right=0.97)

    if np.any(valid_mask):
        ax.plot(lon_d[valid_mask], lat_d[valid_mask],
                lw=2.0, color="gray", zorder=1, alpha=0.5)
        ax.scatter(lon_d[valid_mask], lat_d[valid_mask],
                   s=80, facecolors='white', edgecolors='black',
                   linewidths=1.0, zorder=5)
        ax.scatter(lon_d[valid_mask][0], lat_d[valid_mask][0],
                   marker='*', s=200, color='yellow',
                   edgecolors='black', linewidths=1.0, zorder=10)

    for i in range(len(lon_d)):
        if np.isnan(lon_d[i]) or np.isnan(lat_d[i]):
            continue
        if not np.isnan(uw_scaled[i]) and not np.isnan(vw_scaled[i]):
            ax.quiver(lon_d[i], lat_d[i], uw_scaled[i], vw_scaled[i],
                      scale=1, scale_units="xy", width=0.003,
                      color=WIND_COLOR, alpha=0.9, zorder=3)
        if not np.isnan(uc_scaled[i]) and not np.isnan(vc_scaled[i]):
            ax.quiver(lon_d[i], lat_d[i], uc_scaled[i], vc_scaled[i],
                      scale=1, scale_units="xy", width=0.003,
                      color=CURRENT_COLOR, alpha=0.9, zorder=3)

    for i in range(len(segment_speeds)):
        if not valid_mask[i] or not valid_mask[i + 1]:
            continue
        if np.isnan(segment_speeds[i]):
            continue
        mid_lon = (lon_d[i] + lon_d[i + 1]) / 2
        mid_lat = (lat_d[i] + lat_d[i + 1]) / 2
        dx = lon_d[i + 1] - lon_d[i]
        dy = lat_d[i + 1] - lat_d[i]
        angle = np.degrees(np.arctan2(dy, dx))
        if angle > 90:
            angle -= 180
        elif angle < -90:
            angle += 180
        ax.text(
            mid_lon, mid_lat,
            f"{segment_speeds[i]:.2f} m/s",
            ha='center', va='bottom',
            fontsize=4,
            color='black',
            rotation=angle,
            rotation_mode='anchor',
            zorder=6,
            path_effects=[path_effects.withStroke(linewidth=1.5, foreground='white')]
        )

    if np.any(valid_mask):
        xmin, xmax = np.nanmin(lon_d[valid_mask]), np.nanmax(lon_d[valid_mask])
        ymin, ymax = np.nanmin(lat_d[valid_mask]), np.nanmax(lat_d[valid_mask])
        x_margin = max(spatial_margin, (xmax - xmin) * 0.15)
        y_margin = max(spatial_margin, (ymax - ymin) * 0.15)
        ax.set_xlim(xmin - x_margin, xmax + x_margin)
        ax.set_ylim(ymin - y_margin, ymax + y_margin)
    else:
        ax.set_xlim(lon_min, lon_max)
        ax.set_ylim(lat_min, lat_max)

    ax.xaxis.set_major_formatter(FuncFormatter(
        lambda x, _: f"{abs(x):.5f}°{'E' if x >= 0 else 'W'}"))
    ax.yaxis.set_major_formatter(FuncFormatter(
        lambda y, _: f"{abs(y):.5f}°{'N' if y >= 0 else 'S'}"))
    ax.tick_params(which='both', top=False, right=False,
                   labeltop=False, labelright=False)
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.8)

    CEST = timezone(timedelta(hours=2))
    t0_cest = t0.astimezone(CEST)
    t1_cest = t1.astimezone(CEST)

    ax.set_title(
        'Drone trajectory and wind, current and drone speed vectors from '
        f'{t0_cest.strftime("%Y-%m-%d %H:%M:%S")} to {t1_cest.strftime("%Y-%m-%d %H:%M:%S")} CEST\n'
        f'(Vectors each {node_step} seconds, drone speed limited to {max_drone_speed} m/s)',
        fontsize=14, pad=2
    )

    legend_loc   = find_empty_corner(ax, lon_d, lat_d, valid_mask)
    north_corner = find_empty_corner(ax, lon_d, lat_d, valid_mask,
                                     exclude={legend_loc})
    used_two     = {legend_loc, north_corner}
    scale_corner = next(
        (c for c in ['lower left', 'lower right'] if c not in used_two),
        'lower left'
    )
    all_corners  = {'upper right', 'upper left', 'lower right', 'lower left'}
    key_corner   = next((c for c in all_corners
                         if c not in {legend_loc, north_corner, scale_corner}),
                        'lower right')

    anchor_map = {
        'upper right': (0.98, 0.98),
        'upper left':  (0.02, 0.98),
        'lower right': (0.98, 0.24),
        'lower left':  (0.02, 0.24),
    }
    anchor = anchor_map[legend_loc]
    legend_handles = [
        Line2D([0], [0], color='gray', lw=2, linestyle='-',
               alpha=0.5, label='Trajectory'),
        Patch(facecolor='white', edgecolor='black', label='Node'),
        Line2D([0], [0], marker='*', color='yellow', markerfacecolor='yellow',
               markersize=10, linestyle='None', label='Start'),
        Patch(facecolor=WIND_COLOR,    edgecolor='none', label='Wind vector'),
        Patch(facecolor=CURRENT_COLOR, edgecolor='none', label='Current vector'),
    ]
    legend = ax.legend(handles=legend_handles, loc=legend_loc,
                       bbox_to_anchor=anchor, frameon=True,
                       fontsize=10, framealpha=0.9)

    corner_pos = {
        'upper right': (0.95, 0.88, 0.95, 0.98),
        'upper left':  (0.05, 0.88, 0.05, 0.98),
        'lower right': (0.95, 0.07, 0.95, 0.17),
        'lower left':  (0.05, 0.07, 0.05, 0.17),
    }
    nx_txt, ny_txt, nx_tip, ny_tip = corner_pos[north_corner]
    ax.annotate('N',
                xy=(nx_tip, ny_tip),
                xytext=(nx_txt, ny_txt),
                xycoords='axes fraction', textcoords='axes fraction',
                arrowprops=dict(arrowstyle='-|>', lw=1.5, color='k'),
                ha='center', va='center', fontsize=12,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          alpha=0.8),
                zorder=30)

    x0_ax, x1_ax = ax.get_xlim()
    y0_ax, y1_ax = ax.get_ylim()
    mean_lat_ax  = 0.5 * (y0_ax + y1_ax)
    dx_m         = 111320 * np.cos(np.radians(mean_lat_ax))
    scalebar     = ScaleBar(dx=dx_m, units="m", location=scale_corner,
                            color="black", border_pad=0.5)
    ax.add_artist(scalebar)

    _key_inset, key_bbox_px = draw_vector_key(
        fig, ax, key_corner, REFERENCE_SPEED,
        wind_scale_factor, current_scale_factor,
        vector_scale, meters_per_degree_lon_local
    )

    fig.canvas.draw()

    occupancy = build_density_map(
        ax, fig, lon_d, lat_d, valid_mask,
        uw_scaled, vw_scaled, uc_scaled, vc_scaled
    )

    renderer  = fig.canvas.get_renderer()
    H_occ     = occupancy.shape[0]
    W_occ     = occupancy.shape[1]
    fig_h_px  = fig.get_size_inches()[1] * fig.dpi

    kx0, ky0_fig_bottom, kw, kh = key_bbox_px
    ky0_occ = int(fig_h_px - ky0_fig_bottom - kh)
    ky1_occ = int(fig_h_px - ky0_fig_bottom)
    kx0_occ = int(kx0)
    kx1_occ = int(kx0 + kw)
    occupancy[max(0, ky0_occ):min(H_occ, ky1_occ),
              max(0, kx0_occ):min(W_occ, kx1_occ)] = True

    try:
        legend_bbox = legend.get_window_extent(renderer=renderer)
        PAD = 15
        leg_r0 = H_occ - 1 - int(legend_bbox.y1)
        leg_r1 = H_occ - 1 - int(legend_bbox.y0)
        leg_c0 = int(legend_bbox.x0)
        leg_c1 = int(legend_bbox.x1)
        occupancy[max(0, leg_r0 - PAD):min(H_occ, leg_r1 + PAD),
                  max(0, leg_c0 - PAD):min(W_occ, leg_c1 + PAD)] = True
    except Exception:
        pass

    ax_bbox = ax.get_window_extent(renderer=renderer)
    north_frac_map = {
        'upper right': (0.87, 0.86, 0.12, 0.14),
        'upper left':  (0.01, 0.86, 0.12, 0.14),
        'lower right': (0.87, 0.02, 0.12, 0.17),
        'lower left':  (0.01, 0.02, 0.12, 0.17),
    }
    nf      = north_frac_map[north_corner]
    n_px_x0 = ax_bbox.x0 + nf[0] * ax_bbox.width
    n_px_y0 = ax_bbox.y0 + nf[1] * ax_bbox.height
    n_px_w  = nf[2] * ax_bbox.width
    n_px_h  = nf[3] * ax_bbox.height
    PAD     = 18
    n_r0    = H_occ - 1 - int(n_px_y0 + n_px_h)
    n_r1    = H_occ - 1 - int(n_px_y0)
    n_c0    = int(n_px_x0)
    n_c1    = int(n_px_x0 + n_px_w)
    occupancy[max(0, n_r0 - PAD):min(H_occ, n_r1 + PAD),
              max(0, n_c0 - PAD):min(W_occ, n_c1 + PAD)] = True

    scale_frac_map = {
        'lower left':  (0.01, 0.01, 0.22, 0.06),
        'lower right': (0.77, 0.01, 0.22, 0.06),
        'upper left':  (0.01, 0.93, 0.22, 0.06),
        'upper right': (0.77, 0.93, 0.22, 0.06),
    }
    sf      = scale_frac_map[scale_corner]
    s_px_x0 = ax_bbox.x0 + sf[0] * ax_bbox.width
    s_px_y0 = ax_bbox.y0 + sf[1] * ax_bbox.height
    s_px_w  = sf[2] * ax_bbox.width
    s_px_h  = sf[3] * ax_bbox.height
    s_r0    = H_occ - 1 - int(s_px_y0 + s_px_h)
    s_r1    = H_occ - 1 - int(s_px_y0)
    s_c0    = int(s_px_x0)
    s_c1    = int(s_px_x0 + s_px_w)
    occupancy[max(0, s_r0 - PAD):min(H_occ, s_r1 + PAD),
              max(0, s_c0 - PAD):min(W_occ, s_c1 + PAD)] = True

    existing_boxes      = []
    existing_connectors = []
    valid_node_count    = 0

    for idx in range(len(lon_d)):
        if not valid_mask[idx]:
            continue
        frame = node_frames[idx]
        if frame is None:
            if node_letters[idx]:
                ax.text(lon_d[idx], lat_d[idx], node_letters[idx],
                        ha='center', va='center', fontsize=8, fontweight='bold',
                        color='black', zorder=6,
                        path_effects=[path_effects.withStroke(
                            linewidth=2, foreground='white')])
            continue
        best_offset = find_best_offset(
            ax, fig, lon_d[idx], lat_d[idx],
            existing_boxes, thumb_zoom, occupancy,
            existing_connectors,
            node_index=valid_node_count
        )
        plot_thumbnail_at_node(ax, frame, lon_d[idx], lat_d[idx],
                               zoom=thumb_zoom, offset_points=best_offset)
        valid_node_count += 1

    out_path = os.path.join(OUTPUT_DIR, f"{clip_name}_version6.png")
    fig.savefig(out_path, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out_path}")


##########
## MAIN ##
##########
if __name__ == "__main__":
    for clip_name, (START_EPOCH, END_EPOCH) in VIDEO_CLIPS.items():
        process_clip(clip_name, START_EPOCH, END_EPOCH)