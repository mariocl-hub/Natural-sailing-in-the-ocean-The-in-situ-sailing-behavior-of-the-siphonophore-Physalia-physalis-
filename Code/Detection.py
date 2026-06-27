from ultralytics import YOLO
import cv2

# Cargamos el modelo YOLO
model = YOLO(r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\programación\best_v2.pt")

# Cargamos el video de entrada
video_path = r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\DJI_20250730102351_0004_D\DJI_20250730103517_0004_D.MP4"
cap = cv2.VideoCapture(video_path)

# --- CONFIGURACIÓN DEL VIDEO DE SALIDA ---
output_path = r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\DJI_20250730102351_0004_D\DJI_20250730103517_0004_D_detected.mp4"
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

if not out.isOpened():
    print("❌ ERROR: No se pudo abrir VideoWriter. Comprueba ruta o prueba con otro códec: 'avc1' o 'XVID'")
    exit()
# -----------------------------------------

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Inferencia
    results = model(frame)

    # Frame anotado
    annotated_frame = results[0].plot()

    # GUARDAR EL FRAME
    out.write(annotated_frame)

    # Mostrar en pantalla
    cv2.imshow("YOLO Inference", annotated_frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print("✔ Vídeo guardado como:", output_path)