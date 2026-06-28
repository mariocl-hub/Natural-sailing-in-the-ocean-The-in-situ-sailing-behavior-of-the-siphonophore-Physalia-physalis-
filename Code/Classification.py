from ultralytics import YOLO
import cv2
import csv
from tqdm import tqdm

# --- CONFIGURATION ---
# Update these paths before running
MODEL_PATH  = r"models/best_model_clasifier.pt"
INPUT_VIDEO = r"data/Asturias_analized/Video 3 (30_07_2025_11_30AM)/DJI_20250730114620_0003_D/DJI_20250730114620_0003_D-003_detected_cropped.MP4"
OUTPUT_VIDEO = INPUT_VIDEO.replace(".MP4", "_classified.mp4").replace(".mp4", "_classified.mp4")
OUTPUT_CSV   = OUTPUT_VIDEO.replace(".mp4", ".csv")

model = YOLO(MODEL_PATH)
cap   = cv2.VideoCapture(INPUT_VIDEO)

fps    = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out    = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (width, height))

if not out.isOpened():
    raise RuntimeError(f"Could not open video writer for: {OUTPUT_VIDEO}")

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

with open(OUTPUT_CSV, "w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["frame", "class", "confidence"])

    for frame_id in tqdm(range(total_frames), desc="Classifying frames"):
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        r       = results[0]

        if r.probs is not None:
            cls        = int(r.probs.top1)
            conf       = float(r.probs.top1conf)
            class_name = model.names[cls]
            writer.writerow([frame_id, class_name, conf])

        out.write(r.plot())

cap.release()
out.release()

print(f"Done: {OUTPUT_VIDEO}")
