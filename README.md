# Natural-sailing-in-the-ocean-The-in-situ-sailing-behavior-of-the-siphonophore-Physalia-physalis-
This repository contains all code, figures, databases, videos, and material used in the making of the article  Natural sailing in the ocean: “The in situ sailing behavior of the siphonophore Physalia physalis” by Mario Cabrera-Lavara as student of the University of Oviedo and member of the project PHYSALIA, supervised by Dr. Jose Luis Acuña-Fernandez.

Video data is stored externally due to file size (10 GB). It is separated in 3 .rar files (~3.5GB) that can be accessed from Zenodo: 
> **Zenodo DOI:** [![DOI](https://zenodo.org/badge/DOI/10.5281/10.5281/zenodo.20978184.svg)](https://doi.org/10.5281/zenodo.zenodo.20978184)  

---

## Overview

The dataset consists of drone footage of *Physalia physalis* individuals drifting at the sea surface, collected during fieldwork campaigns on the Cantabrian coast (Asturias, Spain) in July–August 2025. Each video session captures one individual tracked continuously from the air, with derived outputs including bounding-box detections, posture classifications, and motion vector overlays.

---

## Folder structure:
```
Asturias_analized/
│
├── Video 1 (30_07_2025_10AM)/
│   └── [same subfolder structure as Video 5]
├── Video 2 (30_07_2025_11AM)/
│   └── [same subfolder structure as Video 5]
├── Video 3 (30_07_2025_11_30AM)/
│   └── [same subfolder structure as Video 5]
├── Video 4 (30_07_2025_12AM)/
│   └── [same subfolder structure as Video 5]
│
├── Video 5 (20250730_BUCKET#019_drone-camera_DJI_202508041055_005)/
│   ├── DJI_20250804105815_0001_D/
│   │   ├── bbox_per_frame_v2.csv
│   │   ├── DJI_..._detected_cropped.MP4
│   │   ├── DJI_..._detected_cropped_classified.mp4
│   │   ├── DJI_..._detected_cropped_classified_per_second.xlsx
│   │   └── DJI_..._detected_cropped_vector_overlay_5s_bin.mp4
│   ├── DJI_20250804113027_0002_D/
│   ├── DJI_20250804113416_0003_D/
│   ├── DJI_20250804113805_0004_D/
│   └── DJI_20250804114153_0005_D/
│
├── Video 6 (20250730_BUCKET#007_drone-camera_DJI_202508041123_006)/
│   └── [same subfolder structure as Video 5]
│
├── Video 7 (20250730_BUCKET#008_drone-camera_DJI_202508041150_007)/
│   └── [same subfolder structure as Video 5]
│
└── Video 8 (20250730_BUCKET#009_drone-camera_DJI_202508041221_008)/
    └── [same subfolder structure as Video 5]
```
 Auxiliary or complementary files may also be present in non-sequential folders, such as .csv files with classification data or converted .mp4 files

---

## File Descriptions
Each tracking unit is organized in a subfolder named after the DJI clip it originates from (`DJI_{datetime}_{sequence}_D/`), and contains the following files:

| File | Description |
|------|-------------|
| `bbox_per_frame_v2.csv` | Per-frame bounding box coordinates and detection confidence scores exported from the YOLO detection pipeline. |
| `*_detected_cropped.MP4` | Raw drone footage cropped around the detected *Physalia* individual. |
| `*_detected_cropped_classified.mp4` | Cropped footage with posture classification labels overlaid per frame (classes: C_Shape, L_Shape, Upright, Laid_down, Normal). |
| `*_detected_cropped_classified_per_second.xlsx` | Dominant posture class aggregated per second across the clip, used as input for statistical analyses. |
| `*_detected_cropped_vector_overlay_5s_bin.mp4` | Cropped footage with motion vectors (drift direction and speed) overlaid in 5-second temporal bins. |

---

## Naming Conventions
 
**Video-level folders** follow two formats:
- Early sessions: `Video N (DD_MM_YYYY_HHam/pm)`
- Later sessions: `Video N (YYYYMMDD_BUCKET#XXX_drone-camera_DJI_{timestamp}_{session_id})`
**Clip-level subfolders** follow DJI's standard naming:
- `DJI_{YYYYMMDD}{HHMMSS}_{sequence}_D`

---

## How to Use
 
1. Download the `.rar` archive parts from Zenodo (`Asturias_analized.part1.rar`, `.part2.rar`, etc.)
2. Extract using [WinRAR](https://www.rarlab.com/) or [7-Zip](https://www.7-zip.org/) — open `part1.rar` and all parts will be joined automatically
3. Place the extracted `Asturias_analized/` folder in the root of this repository
4. Analysis scripts in `code/` reference this folder by relative path
---
