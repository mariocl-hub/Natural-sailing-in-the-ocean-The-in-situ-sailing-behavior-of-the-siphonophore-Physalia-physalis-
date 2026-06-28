from pydoc import text
from tkinter import font
from tkinter import font
from matplotlib import text

import cv2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import os

####################
# DICTIONARY SETUP #
####################

# Configuración general que no cambia entre videos
DATA_FILE = r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Sensor\Sensor_DataFiles\Global.xlsx"


# Diccionario con todas las configuraciones de videos
VIDEO_CONFIGS = {
    # ===== VIDEO 1 - 30_07_2025_10AM =====
    "video1_clip1": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0001_D\DJI_20250730102351_0001_D_detected_cropped.mp4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0001_D\DJI_20250730102351_0001_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807186231
    },
    "video1_clip2": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0002_D\DJI_20250730102740_0002_D_detected_cropped.mp4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0002_D\DJI_20250730102740_0002_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807186460
    },
    "video1_clip3": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0003_D\DJI_20250730103129_0003_D_detected_cropped.mp4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0003_D\DJI_20250730103129_0003_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807186689
    },
    "video1_clip4": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0004_D\DJI_20250730103517_0004_D_detected_cropped.mp4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 1 (30_07_2025_10AM)\DJI_20250730102351_0004_D\DJI_20250730103517_0004_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807186918
    },
   
    # ===== VIDEO 2 - 30_07_2025_11AM =====
    "video2_clip1": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730110740_0003_D\DJI_20250730110740_0003_D_detected_cropped.MP4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730110740_0003_D\DJI_20250730110740_0003_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807188860
    },
    "video2_clip2": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111129_0004_D\DJI_20250730111129_0004_D_detected_cropped.MP4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111129_0004_D\DJI_20250730111129_0004_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807189089
    },
    "video2_clip3": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111517_0005_D\DJI_20250730111517_0005_D_detected_cropped.mp4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111517_0005_D\DJI_20250730111517_0005_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807189317
    },
    "video2_clip4": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111906_0006_D\DJI_20250730111906_0006_D_detected_cropped.mp4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730111906_0006_D\DJI_20250730111906_0006_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807189546
    },
    "video2_clip5": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730112255_0007_D\DJI_20250730112255_0007_D_detected_cropped.mp4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 2 (30_07_2025_11AM)\DJI_20250730112255_0007_D\DJI_20250730112255_0007_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807189775
    },


    # ===== VIDEO 3 - 30_07_2025_11AM =====
    "video3_clip1": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730113843_0001_D\DJI_20250730113843_0001_D-002_detected_cropped.MP4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730113843_0001_D\DJI_20250730113843_0001_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807190723
    },
    "video3_clip2": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730114231_0002_D\DJI_20250730114231_0002_D-001_detected_cropped.MP4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730114231_0002_D\DJI_20250730114231_0002_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807190952
    },
    "video3_clip3": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730114620_0003_D\DJI_20250730114620_0003_D-003_detected_cropped.MP4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730114620_0003_D\DJI_20250730114620_0003_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807191180
    },
    "video3_clip4": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730115009_0004_D\DJI_20250730115009_0004_D-004_detected_cropped.MP4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730115009_0004_D\DJI_20250730115009_0004_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807191409
    },
    "video3_clip5": {
        "input": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730115358_0005_D\DJI_20250730115358_0005_D-005_detected_cropped.MP4",
        "output": r"C:\Users\Usuario\Documents\Mario\Estudios\Master Universitario\TFM\database\Video 3 (30_07_2025_11_30AM)\DJI_20250730115358_0005_D\DJI_20250730115358_0005_D_detected_cropped_vector_overlay_5s_bin.mp4",
        "epoch": 807191638
    },
}

########################
## BUCLE AUTOMÁTICO ###
########################
for SELECTED_VIDEO, config in VIDEO_CONFIGS.items():
    print(f"Procesando {SELECTED_VIDEO}...")

    VIDEO_IN = config["input"]
    VIDEO_OUT = config["output"]
    VIDEO_START_EPOCH = config["epoch"]

    ##########################
    ## PARÁMETROS GENERALES ##
    ##########################
    BIN_SECONDS = 5  # Duración de cada bin en segundos
    MAX_SPEED = 10.0 #Umbral máximo de velocidad

    #Corrección y visualización (A revisar con sus funciones asociadas)
    APPLY_WIND_CORRECTION = True
    WIND_DISPLAY_MODE = "corrected" # "both", "raw", "corrected"
    WIND_MIN_VALID = 0 # X (m/s): umbral mínimo del viento medido para permitir la corrección

    #Ajustes visuales
    CENTER_COLOR = (255, 255, 255) # Blanco
    FPS_OVERRIDE = None  # Si quieres forzar un FPS específico, pon el valor aquí (ej: 30). Si es None, se usará el FPS del video original.
    CENTER = (320,320) #Coordenadas centro del video (en píxeles)
    SCALE = 25 
    THICKNESS = 3

    COLORS = {
        "wind": (0, 255, 0),  # Verde para el viento corregido
        "current": (255, 0, 0), #Azul para la corriente
        "drone": (0, 0, 255), #Rojo para la trayectoria del dron
        "Expected trajectory": (255, 255, 0) #Amarillo para la trayectoria esperada
    }

    ####################
    ## CARGA DE DATOS ##
    ####################
    if DATA_FILE.lower().endswith('.csv'):
        df = pd.read_csv(DATA_FILE)

    else:   
        df = pd.read_excel(DATA_FILE)

    df = df.sort_values("UTC (Y2K epoch)").reset_index(drop=True) #Aseguramos que los datos estén ordenados por tiempo
    df["datetime UTC (+2)"] = df["datetime UTC (+2)"].astype(str) #Aseguramos que la columna de fecha esté en formato string para luego convertirla a datetime

    required_cols = [
        "UTC (Y2K epoch)", #Tiempo en formato Y2K(segundos desde 1 de enero de 2000)
        "u_wind_raw", "v_wind_raw", #Componentes u y v del viento medido por la boya
        "Sensor_u_drift", "Sensor_v_drift", #Componentes u y v de la deriva medida por la boya
        "u_current", "v_current", #Componentes u y v de la corriente
        "u_drone", "v_drone", #Componentes u y v de la velocidad del dron
        "Lat_drone", "Lon_drone", #Latitud y longitud del dron
    ]

    for c in required_cols:
        if c not in df.columns:
            raise ValueError(f"❌ Falta columna: {c}")

    #############################################################
    ## CONVERSIÓN DE COMPONENTES VECTORIALES Y LAT/LON A FLOAT ##
    #############################################################
    vector_cols = [
        "u_wind_raw", "v_wind_raw",
        "Sensor_u_drift", "Sensor_v_drift",
        "u_current", "v_current",
        "u_drone", "v_drone",
    ]

    for col in vector_cols:
        df[col] = (
            df[col]
            .astype(str) #Convertimos a texto
            .str.replace(",",".", regex = False) #Sustituimos punto por coma
            .replace(to_replace = r"[^\d\.\-]+", value = np.nan, regex = True)
            .astype(float)
        )

    for col in ["Lat_drone", "Lon_drone"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",",".", regex = False)
            .replace(to_replace = r"[^\d\.\-]+", value = np.nan, regex = True)
            .astype(float)
        )

    epochs = df["UTC (Y2K epoch)"].values

    ########################
    ## FILTRO VELOCIDADES ##
    ########################
    def filter_by_speed(df_local, u_col, v_col, vmax):
        speed = np.hypot(df_local[u_col], df_local[v_col])
        mask = speed > vmax
        df_local.loc[mask, [u_col, v_col]] = np.nan

    filter_by_speed(df, "u_wind_raw", "v_wind_raw", MAX_SPEED)
    filter_by_speed(df, "u_wind_corrected", "v_wind_corrected", MAX_SPEED)
    filter_by_speed(df, "u_current", "v_current", MAX_SPEED)
    filter_by_speed(df, "u_drone", "v_drone", MAX_SPEED)

    ########################
    ## CÁLCULO DE MÓDULOS ##
    ########################
    df["wind_speed_raw"] = np.hypot(df["u_wind_raw"], df["v_wind_raw"])
    df["wind_speed_corrected"] = np.hypot(df["u_wind_corrected"], df["v_wind_corrected"])
    df["current_speed"] = np.hypot(df["u_current"], df["v_current"])
    df["drone_speed"] = np.hypot(df["u_drone"], df["v_drone"])

    ######################################
    ## CALCULAMOS VELOCIDAD A 10 METROS ##
    ######################################
    #Nuestro dispositivo está a 0.525 metros, necesitamos a 10 metros
    #por estándar, así calculamos la trayectoria de Bourg

    #z0 y sus velocidades empíricas
    wind_speeds_ref = np.array([1, 2, 4, 6, 7, 8, 10, 12])  # m/s
    z0_ref = np.array([4.71, 6.60, 27.2, 38.3, 43.3, 48.3, 72.1, 95.9]) * 1e-5

    #Función para usar la z0 más cercana
    def get_z0(ws):
        idx = np.abs(wind_speeds_ref - ws).argmin()
        return z0_ref[idx]

    # Compute z0 per row
    df["z0"] = [get_z0(ws) for ws in df["wind_speed_corrected"]]

    # Compute wind at 10 m per row
    df["wind_speed_10m"] = df["wind_speed_corrected"] * (
        np.log(10 / df["z0"]) / np.log(0.525 / df["z0"])
    )

    ######################
    ## BOURG TRAJECTORY ##
    ######################
    ##Here I have to add the formula to calculate the expected trajectory from
    #Bourgs formula, in order to show the expected and observed trajectory
    #Alpha = (50.8e**(-0.15*wind_speed_10m))-0.5
    df['expected_trajectory'] = 50.8 * np.exp(-0.15 * df['wind_speed_10m']) - 0.5
    """print("✅ Cálculo de trayectoria de Bourg completado.")
    print(df[["wind_speed_10m", "expected_trajectory"]].head())"""

    ######################
    ## BINNING TEMPORAL ##
    ######################
    t0 = epochs.min()
    df["time_bin"] = ((df["UTC (Y2K epoch)"] - t0) // BIN_SECONDS).astype(int)

    bin_means = (
        df
        .groupby("time_bin")
        .agg(
            #Raw wind
            u_wind_raw = ("u_wind_raw", "mean"),
            v_wind_raw = ("v_wind_raw", "mean"),
            wind_speed_raw = ("wind_speed_raw", "mean"),
            
            #Corrected wind
            u_wind_corrected = ("u_wind_corrected", "mean"),
            v_wind_corrected = ("v_wind_corrected", "mean"),
            wind_speed_corrected = ("wind_speed_corrected", "mean"),

            #Current
            u_current = ("u_current", "mean"),
            v_current = ("v_current", "mean"),
            current_speed = ("current_speed", "mean"),

            #Drone
            u_drone = ("u_drone", "mean"),
            v_drone = ("v_drone", "mean"),
            drone_speed = ("drone_speed", "mean"),

            # texto/tiempo representativo
            datetime=("datetime UTC (+2)", "first"),
            epoch_mean=("UTC (Y2K epoch)", "mean"),

            #Bourg
            bourg_direction = ("expected_trajectory", "mean"),            
        )
        .reset_index()
    )

    #Total bin number
    total_bins = int(bin_means["time_bin"].nunique())

    ####################
    ## VIDEO - CONFIG ##
    ####################
    cap = cv2.VideoCapture(VIDEO_IN)
    if not cap.isOpened():
        raise IOError(f"❌ No se pudo abrir el video: {VIDEO_IN}")

    fps = FPS_OVERRIDE or cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(VIDEO_OUT, fourcc, fps, (w, h))

    #########################
    ## FUNCIONES DE DIBUJO ##
    #########################
    def draw_solid_arrow(frame, start, end, color, thickness = 2, tip_length = 0.2):
        cv2.arrowedLine(frame, start, end, color, thickness, tipLength = tip_length)

    def draw_vector_at_center(frame, u, v, color, scale = 1.0, dashed = False):
        #u: componente Este (x), v: componente Norte (y). En pantalla dy se resta porque Y aumenta hacia abajo.
        if u is None or v is None or np.isnan(u) or np.isnan(v):
            return np.nan
        dx = u * scale
        dy = v * scale
        start = (int(round(CENTER[0])), int(round(CENTER[1])))
        end = (int(round(CENTER[0] + dx)), int(round(CENTER[1] - dy)))
        draw_solid_arrow(frame, start, end, color, thickness = THICKNESS)
        return np.hypot(u, v)

    def draw_bourg_direction(frame, angle_deg, color, length=80):
        if np.isnan(angle_deg):
            return

        angle_rad = np.radians(angle_deg)

        dx = length * np.sin(angle_rad)
        dy = length * np.cos(angle_rad)

        start = CENTER
        end = (
            int(CENTER[0] + dx),
            int(CENTER[1] - dy)
        )

        cv2.arrowedLine(
            frame,
            start,
            end,
            color,
            3,
            tipLength=0.2
        )

    def put_text_with_bg(
        frame,
        text,
        org,
        font=cv2.FONT_HERSHEY_SIMPLEX,
        font_scale=0.45,
        text_color=(0, 0, 0),
        bg_color=(255, 255, 255),
        thickness=1,
        padding=4
    ):
        """
        Dibuja texto con un recuadro de fondo.
        org = (x, y) es la esquina inferior izquierda del texto (como putText)
        """
        (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)


        x, y = org


        # Coordenadas del rectángulo
        top_left = (x - padding, y - text_h - padding)
        bottom_right = (x + text_w + padding, y + baseline + padding)


        # Rectángulo relleno
        cv2.rectangle(frame, top_left, bottom_right, bg_color, -1)


        # Texto encima
        cv2.putText(
            frame,
            text,
            org,
            font,
            font_scale,
            text_color,
            thickness,
            cv2.LINE_AA
        )

    #####################
    ## BUCLE PRINCIPAL ##
    #####################
    frame_idx = 0
    DRONE_VISUAL_SCALE = 20.0

    #Texto
    mode_txt = (
        "MODE: BOTH (corregido solido / raw punteado)" if WIND_DISPLAY_MODE == "both"
        else ("MODE: RAW (solo raw punteado)" if WIND_DISPLAY_MODE == "raw"
            else "MODE: CORRECTED (solo corregido solido)")
    )

    while True:
        ret, frame = cap.read ()
        if not ret:
            break

        frame_epoch = VIDEO_START_EPOCH + frame_idx / fps
        bin_idx = int((frame_epoch -t0) // BIN_SECONDS)

        row_bin = bin_means[bin_means["time_bin"] == bin_idx]

        if row_bin.empty:
            # mostrar modo y bins aunque no haya datos para este bin
            cv2.putText(frame, mode_txt, (10, h - 55), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200,200,200), 1)
            cv2.putText(frame, f"Bins totales: {total_bins}", (10, h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200,200,200), 1)
            cv2.putText(frame, f"Bin idx: {bin_idx}", (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200,200,200), 1)


            out.write(frame)
            frame_idx += 1
            continue

        row = row_bin.iloc[0]

        cv2.circle(frame, CENTER, 4, CENTER_COLOR, -1)

        # --- viento (tiene componentes negativas para que apunte en la dirección correcta)
        u_corr = row.u_wind_corrected
        v_corr = row.v_wind_corrected
        mag_corr = draw_vector_at_center(frame, -u_corr, -v_corr, COLORS["wind"], SCALE, dashed=False)


        # --- corriente y dron
        mag_current = draw_vector_at_center(frame, row.u_current, row.v_current, COLORS["current"], SCALE)
        mag_drone = draw_vector_at_center(frame, row.u_drone, row.v_drone, COLORS["drone"], SCALE * DRONE_VISUAL_SCALE)

        """# --- bourg
        if not pd.isna(row.bourg_direction):
            draw_bourg_direction(
                frame,
                row.bourg_direction,
                COLORS["Expected trajectory"]
            )"""

        # texto cabecera: epoch y datetime
        cv2.putText(frame, f"UTC epoch: {frame_epoch:.2f}", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


        cv2.putText(frame, "Fecha/hora (UTC+2):", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)


        cv2.putText(frame, str(row["datetime"]), (10, 52),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)
    
        y0 = 75
        dy = 18

        ### VIENTO
        if not pd.isna(row.wind_speed_corrected):
            net_corr = mag_corr if not np.isnan(mag_corr) else np.nan
            put_text_with_bg(
                frame,
                f"Viento CORR: {row.wind_speed_corrected:.2f} m/s | neto {net_corr:.2f}",
                (10, y0),
                text_color=COLORS["wind"],
                bg_color=(255, 255, 255)
            )
        else:
            if not APPLY_WIND_CORRECTION:
                put_text_with_bg(
                    frame,
                    "Viento CORR: corrección DESHAB.",
                    (10, y0),
                    text_color=(150, 150, 150),
                    bg_color=(255, 255, 255)
                )
            else:
                put_text_with_bg(
                    frame,
                    f"Viento CORR: No observable (apparent < {WIND_MIN_VALID} m/s)",
                    (10, y0),
                    text_color=(150, 150, 150),
                    bg_color=(255, 255, 255)
                )
        y0 += dy

        ### CORRIENTE
        if not pd.isna(row.current_speed):
            net = mag_current if not np.isnan(mag_current) else np.nan
            put_text_with_bg(
                frame,
                f"Corriente: {row.current_speed:.2f} m/s | neto {net:.2f}",
                (10, y0),
                text_color=COLORS["current"],
                bg_color=(255, 255, 255)
            )
            y0 += dy

        ### DRON
        if not pd.isna(row.drone_speed):
            net = mag_drone if not np.isnan(mag_drone) else np.nan
            put_text_with_bg(
                frame,
                f"Dron: {row.drone_speed:.2f} m/s | neto {net:.2f}",
                (10, y0),
                text_color=COLORS["drone"],
                bg_color=(255, 255, 255)
            )
            y0 += dy

        ### BOURG ANGLE
        """if not pd.isna(row.bourg_direction):
            angle = row.bourg_direction % 360  # asegura rango 0-360

            put_text_with_bg(
                frame,
                f"Angulo Bourg: {angle:.1f}°",
                (10, y0),
                text_color=(255, 255, 0),  # amarillo
                bg_color=(255, 255, 255)
            )
        y0 += dy"""

        # Binneo empleado
        cv2.putText(
        frame,
        f"Promediado temporal: {BIN_SECONDS} s (binning)",
        (10, h - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (200, 200, 200),
        1
        )

        out.write(frame)
        frame_idx += 1

    ############
    ## CIERRE ##
    ############
    cap.release()
    out.release()
    print(f"✅ Video procesado y guardado en: {VIDEO_OUT}") 