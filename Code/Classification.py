from ultralytics import YOLO
import cv2
import csv
from tqdm import tqdm

#Load YOLO model
model = YOLO(r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\programación\best_model_clasifier.pt")

#Open video
video_path = r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730114620_0003_D\DJI_20250730114620_0003_D-003_detected_cropped.MP4"
cap = cv2.VideoCapture(video_path)

#Video output settings
output_path = r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730114620_0003_D\DJI_20250730114620_0003_D_detected_cropped_classified.csv"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

if not out.isOpened():
    print("Error: Could not open video for writing.")
    exit()

while cap.isOpened():
    #CSV setup for results
    csv_path = output_path.replace(".mp4", ".csv")
    csv_file = open(csv_path, "w", newline="")
    writer = csv.writer(csv_file)
    writer.writerow(["frame", "class", "confidence"])

    #Progress bar setup
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    #Progress bar loop for YOLO inference
    for frame_id in tqdm(range(total_frames), desc="Processing frames"):
        ret, frame = cap.read()
        if not ret:
            break
    
    #Usual YOLO inference loop
    #while cap.isOpened():
    #    ret, frame = cap.read()
    #    if not ret:
    #        break

        # YOLO inference
        results = model(frame)
        r = results[0]

        if r.probs is not None:
            cls = int(r.probs.top1)
            conf = float(r.probs.top1conf)
            class_name = model.names[cls]

            writer.writerow([frame_id, class_name, conf])

        annotated_frame = r.plot()

        # Save frame
        out.write(annotated_frame)

        # Optional preview, commented out for efficiency
        """cv2.imshow("YOLO Inference", annotated_frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break"""

    cap.release()
    out.release()
    csv_file.close()
    #cv2.destroyAllWindows() #Comentado para evitar errores en entornos sin GUI

    print(f"Finished: {output_path}")