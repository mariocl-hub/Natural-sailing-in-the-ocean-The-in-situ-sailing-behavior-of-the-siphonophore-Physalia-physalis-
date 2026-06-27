from ultralytics import YOLO
import cv2
import numpy as np
import csv
import os

# --- CONFIG ---
MODEL_PATH = r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\programación\best_v2.pt"
INPUT_VIDEO = r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111517_0005_D\DJI_20250730111517_0005_D.MP4"
OUTPUT_VIDEO = r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111517_0005_D\DJI_20250730111517_0005_D_detected_cropped.MP4"
OUTPUT_CSV = r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111517_0005_D\bbox_per_frame_v2.csv"

# Tamaño final de los recortes (ancho, alto)
OUTPUT_SIZE = (640, 640)

# Padding relativo a la bbox (0.0 = sin padding, 0.2 = 20% extra)
PADDING_REL = 0.2

# Estrategia si hay varias detecciones: "largest" (por área) o "union"
MODE = "largest"
# ----------------

# Carga modelo
model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(INPUT_VIDEO)
if not cap.isOpened():
    raise RuntimeError(f"No se pudo abrir el vídeo {INPUT_VIDEO}")

fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, OUTPUT_SIZE)

# Prepara CSV
csv_file = open(OUTPUT_CSV, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["frame_idx", "x1", "y1", "x2", "y2", "conf"])

frame_idx = 0
last_box = None  # fallback si no hay detecciones en un frame

height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

print("Procesando... pulsa ESC en la ventana para detener manualmente.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # inferencia
    results = model(frame)

    # intentamos extraer cajas (xyxy) y confidencias
    boxes_arr = None
    confs = None
    try:
        xyxy = results[0].boxes.xyxy  # tensor-like
        if hasattr(xyxy, "cpu"):
            boxes_arr = xyxy.cpu().numpy()
        else:
            boxes_arr = np.array(xyxy)

        conf = results[0].boxes.conf
        if hasattr(conf, "cpu"):
            confs = conf.cpu().numpy()
        else:
            confs = np.array(conf)
    except Exception:
        boxes_arr = np.zeros((0, 4))
        confs = np.zeros((0,))

    chosen_box = None
    chosen_conf = 0.0

    if boxes_arr is not None and boxes_arr.size > 0:
        if MODE == "largest":
            areas = (boxes_arr[:, 2] - boxes_arr[:, 0]) * (boxes_arr[:, 3] - boxes_arr[:, 1])
            idx = int(np.argmax(areas))
            x1, y1, x2, y2 = boxes_arr[idx].astype(int)
            chosen_conf = float(confs[idx]) if confs is not None and confs.size > idx else 0.0
            chosen_box = (x1, y1, x2, y2)
        elif MODE == "union":
            x1 = int(np.min(boxes_arr[:, 0]))
            y1 = int(np.min(boxes_arr[:, 1]))
            x2 = int(np.max(boxes_arr[:, 2]))
            y2 = int(np.max(boxes_arr[:, 3]))
            chosen_box = (x1, y1, x2, y2)
            chosen_conf = float(np.max(confs)) if confs is not None else 0.0

    if chosen_box is not None:
        x1, y1, x2, y2 = chosen_box
        # aplicar padding relativo
        w = x2 - x1
        h = y2 - y1
        pad = int(max(w, h) * PADDING_REL)
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(width - 1, x2 + pad)
        y2 = min(height - 1, y2 + pad)
        last_box = (x1, y1, x2, y2)
    else:
        # No detección: fallback a la última caja válida si existe, si no usar todo el frame
        if last_box is not None:
            x1, y1, x2, y2 = last_box
        else:
            x1, y1, x2, y2 = 0, 0, width - 1, height - 1
        chosen_conf = 0.0

    # Guarda coords en CSV (coordenadas tal cual usadas)
    csv_writer.writerow([frame_idx, x1, y1, x2, y2, f"{chosen_conf:.4f}"])

    # recorta y redimensiona al tamaño de salida fijo
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        # protección: si por alguna razón el recorte es vacío, usar frame completo
        crop = frame
    resized = cv2.resize(crop, OUTPUT_SIZE)

    out.write(resized)

    # Muestra en pantalla (opcional)
    display_frame = resized.copy()
    cv2.putText(display_frame, f"Frame {frame_idx}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    cv2.imshow("Cropped (press ESC to stop)", display_frame)
    if cv2.waitKey(1) & 0xFF == 27:
        print("Interrupción manual por ESC.")
        break

    frame_idx += 1

# Cleanup
cap.release()
out.release()
csv_file.close()
cv2.destroyAllWindows()
print(f"Terminado. Vídeo guardado como: {OUTPUT_VIDEO}")
print(f"CSV de cajas guardado como: {OUTPUT_CSV}")