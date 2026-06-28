from ultralytics import YOLO
import cv2

# --- CONFIGURATION ---
# Update these paths before running
MODEL_PATH  = r"models/best_v2.pt"
INPUT_VIDEO = r"data/Asturias_analized/Video 1 (30_07_2025_10AM)/DJI_20250730102351_0004_D/DJI_20250730103517_0004_D.MP4"
OUTPUT_VIDEO = INPUT_VIDEO.replace(".MP4", "_detected.mp4").replace(".mp4", "_detected.mp4")

model = YOLO(MODEL_PATH)
cap   = cv2.VideoCapture(INPUT_VIDEO)

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps    = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (width, height))
if not out.isOpened():
    raise RuntimeError(
        "Could not open VideoWriter. Check the output path or try a different codec ('avc1', 'XVID')."
    )

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results        = model(frame)
    annotated_frame = results[0].plot()
    out.write(annotated_frame)

    cv2.imshow("YOLO Inference", annotated_frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Video saved: {OUTPUT_VIDEO}")
