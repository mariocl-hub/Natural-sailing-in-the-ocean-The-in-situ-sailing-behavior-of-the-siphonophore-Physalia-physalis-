from ultralytics import YOLO
import cv2
import numpy as np
import csv

# --- CONFIGURATION ---
# Update these paths before running
MODEL_PATH   = r"models/best_v2.pt"
INPUT_VIDEO  = r"data/Asturias_analized/Video 2 (30_07_2025_11AM)/DJI_20250730111517_0005_D/DJI_20250730111517_0005_D.MP4"
OUTPUT_VIDEO = INPUT_VIDEO.replace(".MP4", "_detected_cropped.MP4")
OUTPUT_CSV   = INPUT_VIDEO.replace(".MP4", "_bbox_per_frame_v2.csv")

# Fixed output crop size (width, height)
OUTPUT_SIZE = (640, 640)

# Relative padding around the bounding box (0.0 = none, 0.2 = 20% extra on each side)
PADDING_REL = 0.2

# How to handle multiple detections: "largest" (by area) or "union" (bounding union)
MODE = "largest"

# --- MAIN ---
model = YOLO(MODEL_PATH)
cap   = cv2.VideoCapture(INPUT_VIDEO)
if not cap.isOpened():
    raise RuntimeError(f"Could not open video: {INPUT_VIDEO}")

fps    = cap.get(cv2.CAP_PROP_FPS) or 30.0
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out    = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, OUTPUT_SIZE)

height_f = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
width_f  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

csv_file   = open(OUTPUT_CSV, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["frame_idx", "x1", "y1", "x2", "y2", "conf"])

frame_idx = 0
last_box  = None  # fallback when a frame has no detection

print("Processing... press ESC in the preview window to stop early.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    boxes_arr = None
    confs     = None
    try:
        xyxy = results[0].boxes.xyxy
        boxes_arr = xyxy.cpu().numpy() if hasattr(xyxy, "cpu") else np.array(xyxy)
        conf      = results[0].boxes.conf
        confs     = conf.cpu().numpy() if hasattr(conf, "cpu") else np.array(conf)
    except Exception:
        boxes_arr = np.zeros((0, 4))
        confs     = np.zeros((0,))

    chosen_box  = None
    chosen_conf = 0.0

    if boxes_arr is not None and boxes_arr.size > 0:
        if MODE == "largest":
            areas = (boxes_arr[:, 2] - boxes_arr[:, 0]) * (boxes_arr[:, 3] - boxes_arr[:, 1])
            idx   = int(np.argmax(areas))
            x1, y1, x2, y2 = boxes_arr[idx].astype(int)
            chosen_conf = float(confs[idx]) if confs is not None and confs.size > idx else 0.0
            chosen_box  = (x1, y1, x2, y2)
        elif MODE == "union":
            x1 = int(np.min(boxes_arr[:, 0]))
            y1 = int(np.min(boxes_arr[:, 1]))
            x2 = int(np.max(boxes_arr[:, 2]))
            y2 = int(np.max(boxes_arr[:, 3]))
            chosen_box  = (x1, y1, x2, y2)
            chosen_conf = float(np.max(confs)) if confs is not None else 0.0

    if chosen_box is not None:
        x1, y1, x2, y2 = chosen_box
        w   = x2 - x1
        h   = y2 - y1
        pad = int(max(w, h) * PADDING_REL)
        x1  = max(0, x1 - pad)
        y1  = max(0, y1 - pad)
        x2  = min(width_f - 1, x2 + pad)
        y2  = min(height_f - 1, y2 + pad)
        last_box = (x1, y1, x2, y2)
    else:
        # No detection: reuse last known box, or fall back to full frame
        if last_box is not None:
            x1, y1, x2, y2 = last_box
        else:
            x1, y1, x2, y2 = 0, 0, width_f - 1, height_f - 1
        chosen_conf = 0.0

    csv_writer.writerow([frame_idx, x1, y1, x2, y2, f"{chosen_conf:.4f}"])

    crop    = frame[y1:y2, x1:x2]
    if crop.size == 0:
        crop = frame  # safety fallback if crop is empty
    resized = cv2.resize(crop, OUTPUT_SIZE)

    out.write(resized)

    display = resized.copy()
    cv2.putText(display, f"Frame {frame_idx}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.imshow("Cropped (press ESC to stop)", display)
    if cv2.waitKey(1) & 0xFF == 27:
        print("Stopped early.")
        break

    frame_idx += 1

cap.release()
out.release()
csv_file.close()
cv2.destroyAllWindows()

print(f"Video saved: {OUTPUT_VIDEO}")
print(f"BBox CSV saved: {OUTPUT_CSV}")
