# =============================================================================
# ANÁLISIS DE VELOCIDADES Y CLASES POR VÍDEO
# =============================================================================
# Columnas usadas:
#   UTC (Y2K epoch)    -> identifica el vídeo (agrupado por epoch)
#   datetime UTC (+2)  -> para referencia temporal
#   u_wind_corrected, v_wind_corrected  -> viento corregido
#   u_wind_raw, v_wind_raw              -> viento bruto
#   u_current, v_current               -> corriente marina
#   u_drone, v_drone                   -> movimiento del dron
#   Dominant Class, Confidence, All classes -> clasificación
# =============================================================================

# ── Paquetes ──────────────────────────────────────────────────────────────────
pkgs <- c("readxl", "dplyr", "tidyr", "ggplot2", "ggpubr",
          "nortest", "car", "stringr", "RColorBrewer", "scales", "circular")
for (p in pkgs) {
  if (!requireNamespace(p, quietly = TRUE)) install.packages(p)
  library(p, character.only = TRUE)
}

# ── 1. CARGA DE DATOS ─────────────────────────────────────────────────────────
file_path <- file.choose()   # selecciona tu Excel

# col_types por posición (23 columnas):
#  1  UTC (Y2K epoch)    -> numeric
#  2  datetime UTC (+2)  -> date
#  3-16 variables numéricas
#  17-18 Lat_drone / Lon_drone -> text (contienen "No drone flight log" + números)
#  19-20 u_drone / v_drone    -> numeric
#  21 Dominant Class           -> text
#  22 Confidence               -> numeric
#  23 All classes              -> text
df <- read_excel(
  file_path,
  col_types = c(
    "numeric",                          # 1  UTC (Y2K epoch)
    "date",                             # 2  datetime UTC (+2)
    rep("numeric", 16),                 # 3-16 variables de viento, corriente
    "text", "text",                     # 17-18 Lat_drone, Lon_drone
    "numeric", "numeric",               # 19-20 u_drone, v_drone
    "text",                             # 21 Dominant Class
    "numeric",                          # 22 Confidence
    "text"                              # 23 All classes
  )
)

# Limpieza de nombres de columna (espacios -> guión bajo)
names(df) <- make.names(names(df), unique = TRUE)

# Lat_drone y Lon_drone son mixtas ("No drone flight log" + coords numéricas)
# Convertir a numérico: el texto queda como NA automáticamente
df <- df %>%
  mutate(
    Lat_drone = suppressWarnings(as.numeric(Lat_drone)),
    Lon_drone = suppressWarnings(as.numeric(Lon_drone))
  )

# Muestra columnas disponibles y tipos
cat("Columnas del archivo y tipos:\n")
print(sapply(df, class))

# ── 1b. DETECCIÓN TEMPRANA DE COLUMNAS CLAVE ─────────────────────────────────
epoch_col    <- grep("UTC.*Y2K|epoch", names(df), ignore.case = TRUE, value = TRUE)[1]
datetime_col <- grep("datetime",       names(df), ignore.case = TRUE, value = TRUE)[1]
class_col    <- grep("Dominant.Class|Dominant_Class|DominantClass",
                     names(df), ignore.case = TRUE, value = TRUE)[1]
conf_col     <- grep("Confidence",     names(df), ignore.case = TRUE, value = TRUE)[1]

cat("\nColumna epoch detectada:         ", epoch_col, "\n")
cat("Columna datetime detectada:       ", datetime_col, "\n")
cat("Columna clase dominante detectada:", class_col, "\n")
cat("Columna confianza detectada:      ", conf_col, "\n")

# ── 1c. ASIGNACIÓN DE VIDEO_LABEL (necesaria antes del binning) ───────────────
# Cada entrada: nombre_video = c(epoch_inicio, epoch_fin)  [ambos inclusivos]
video_ranges <- list(
  Video_01 = c(807179031, 807179788),
  Video_02 = c(807181660, 807182709),
  Video_03 = c(807183523, 807184587),
  Video_04 = c(807184906, 807185592),
  Video_05 = c(807613096,807614128),
  Video_06 = c(807614788,807615828),
  Video_07 =  c(807616389,807617440),
  Video_08 = c(807618280,807618998)
)

assign_video <- function(epoch_vals, ranges) {
  label <- rep(NA_character_, length(epoch_vals))
  for (vname in names(ranges)) {
    rng <- ranges[[vname]]
    label[epoch_vals >= rng[1] & epoch_vals <= rng[2]] <- vname
  }
  label
}

df <- df %>%
  arrange(.data[[epoch_col]]) %>%
  mutate(
    video_label = assign_video(.data[[epoch_col]], video_ranges),
    video_id    = as.integer(factor(video_label, levels = names(video_ranges)))
  )

cat("\nVídeos asignados (pre-binning):", n_distinct(df$video_id, na.rm = TRUE), "\n")
cat("Filas dentro de un vídeo:", sum(!is.na(df$video_label)), "\n")
cat("Filas entre vídeos (sin asignar):", sum(is.na(df$video_label)), "\n\n")
print(table(df$video_label, useNA = "no"))


# ── RECLASIFICACIÓN DE VÍDEOS EN SESIONES ────────────────────────────────────
reclasificar_sesion <- function(video_label) {
  dplyr::case_when(
    video_label %in% c("Video_01","Video_02","Video_03","Video_04") ~ "ID.1",
    video_label == "Video_05" ~ "ID.2",
    video_label == "Video_06" ~ "ID.3",
    video_label == "Video_07" ~ "ID.4",
    video_label == "Video_08" ~ "ID.5",
    TRUE ~ NA_character_
  )
}

df <- df %>%
  mutate(
    ID_label = factor(reclasificar_sesion(video_label),
                           levels = c("ID.1","ID.2","ID.3","ID.4","ID.5"))
  )

# ── 1d. BINNING TEMPORAL ──────────────────────────────────────────────────────
BIN_SECONDS <- 5

t0_global <- min(df[[epoch_col]], na.rm = TRUE)

df <- df %>%
  mutate(
    time_bin = as.integer(floor((.data[[epoch_col]] - t0_global) / BIN_SECONDS))
  )

cols_bin <- c(
  "u_wind_raw",       "v_wind_raw",
  "u_wind_corrected", "v_wind_corrected",
  "Sensor_u_drift",   "Sensor_v_drift",
  "u_current",        "v_current",
  "u_drone",          "v_drone"
)
cols_bin <- cols_bin[cols_bin %in% names(df)]

bin_means <- df %>%
  group_by(time_bin) %>%
  summarise(
    across(all_of(cols_bin), ~ mean(.x, na.rm = TRUE)),
    !!epoch_col     := mean(.data[[epoch_col]], na.rm = TRUE),
    video_label     = {
      tbl <- table(video_label[!is.na(video_label)])
      if (length(tbl) == 0) NA_character_ else names(which.max(tbl))
    },
    n_rows_in_bin   = n(),
    .groups = "drop"
  )

# video_id
bin_means <- bin_means %>%
  mutate(
    video_id = as.integer(factor(video_label, levels = names(video_ranges)))
  )

bin_means <- bin_means %>%
  mutate(
    ID_label = factor(reclasificar_sesion(video_label),
                           levels = c("ID.1","ID.2","ID.3","ID.4","ID.5"))
  )

# datetime
if (!is.null(datetime_col) && datetime_col %in% names(df)) {
  dt_first <- df %>%
    group_by(time_bin) %>%
    summarise(!!datetime_col := first(.data[[datetime_col]]), .groups = "drop")
  bin_means <- left_join(bin_means, dt_first, by = "time_bin")
}

# Dominant Class (moda por bin)
if (!is.null(class_col) && class_col %in% names(df)) {
  class_mode <- df %>%
    group_by(time_bin) %>%
    summarise(
      !!class_col := {
        x <- .data[[class_col]][!is.na(.data[[class_col]])]
        if (length(x) == 0) NA_character_ else names(which.max(table(x)))
      },
      .groups = "drop"
    )
  bin_means <- left_join(bin_means, class_mode, by = "time_bin")
}

# Confidence (media por bin)
if (!is.null(conf_col) && conf_col %in% names(df)) {
  conf_mean <- df %>%
    group_by(time_bin) %>%
    summarise(
      !!conf_col := mean(.data[[conf_col]], na.rm = TRUE),
      .groups = "drop"
    )
  bin_means <- left_join(bin_means, conf_mean, by = "time_bin")
}

cat(sprintf("\nBinning temporal: BIN_SECONDS = %d s\n", BIN_SECONDS))
cat(sprintf("  Filas originales : %d\n", nrow(df)))
cat(sprintf("  Bins resultantes : %d\n", nrow(bin_means)))
cat(sprintf("  Reducción        : %.1f%%\n",
            (1 - nrow(bin_means) / nrow(df)) * 100))

df <- bin_means

# ── 2. IDENTIFICACIÓN DE COLUMNAS Y ASIGNACIÓN DE VÍDEOS POR EPOCH ──────────
cat("\nColumna epoch detectada:         ", epoch_col, "\n")
cat("Columna datetime detectada:       ", datetime_col, "\n")
cat("Columna clase dominante detectada:", class_col, "\n")
cat("Columna confianza detectada:      ", conf_col, "\n")

# ── Rangos de epoch para cada vídeo completo ─────────────────────────────────
n_videos    <- n_distinct(df$video_id,    na.rm = TRUE)
n_con_video <- sum(!is.na(df$video_label))
n_sin_video <- sum( is.na(df$video_label))

cat("\nPost-binning — Vídeos asignados:", n_videos, "\n")
cat("Bins dentro de un vídeo:", n_con_video, "\n")
cat("Bins entre vídeos (sin asignar):", n_sin_video, "\n\n")
print(table(df$video_label, useNA = "no"))

# ── RECLASIFICACIÓN: fusión de strict/mild ────────────────────────────────────
reclasificar <- function(x) {
  x <- as.character(x)
  x[x %in% c("C_Shape_strict", "C_Shape_mild")] <- "C_Shape"
  x[x %in% c("L_Shape_strict", "L_Shape_mild")] <- "L_Shape"
  x
}

df[[class_col]] <- reclasificar(df[[class_col]])

# ── 3. CÁLCULO DE VELOCIDADES RESULTANTES Y FILTRO DE ANOMALÍAS ──────────────

# 3a. Velocidades brutas (módulo de cada par de componentes)
df <- df %>%
  mutate(
    speed_wind_corrected = sqrt(u_wind_corrected^2 + v_wind_corrected^2),
    speed_wind_raw       = sqrt(u_wind_raw^2       + v_wind_raw^2),
    speed_current        = sqrt(u_current^2        + v_current^2),
    speed_drone          = sqrt(u_drone^2          + v_drone^2)
  )

# 3b. Filtro de valores anómalos
# Método: se anulan a NA los valores que superen el umbral absoluto físicamente
# razonable O superen Q3 + 3·IQR calculado por vídeo (fence de Tukey extremo).
# El viento bruto (speed_wind_raw) está limpio (máx 6.9 m/s) y no se filtra.
#
# Umbrales absolutos de seguridad (basados en la distribución observada):
#   viento corregido : 20 m/s  (salto natural de 10 → 21 m/s en los datos)
#   corriente marina : 20 m/s  (salto natural de 16 → 23 m/s en los datos)
#   dron             : 20 m/s  (salto natural de 19.9 → 13 610 m/s en los datos)

TECHO_WIND_CORR <- 20   # m/s
TECHO_CURRENT   <- 20   # m/s
TECHO_DRONE     <- 20   # m/s

# Función: aplica techo absoluto + fence IQR×3 por vídeo
filtrar_velocidad <- function(speed_vec, video_vec, techo) {
  out <- speed_vec
  # 1. Techo absoluto
  out[!is.na(out) & out > techo] <- NA_real_
  # 2. Fence de Tukey extremo (Q3 + 3·IQR) por vídeo
  videos <- unique(video_vec[!is.na(video_vec)])
  for (v in videos) {
    idx <- !is.na(video_vec) & video_vec == v
    x   <- out[idx]
    if (sum(!is.na(x)) < 4) next          # demasiado pocos datos
    Q1  <- quantile(x, 0.25, na.rm = TRUE)
    Q3  <- quantile(x, 0.75, na.rm = TRUE)
    fence <- Q3 + 3 * (Q3 - Q1)
    out[idx & !is.na(out) & out > fence] <- NA_real_
  }
  out
}

df <- df %>%
  mutate(
    speed_wind_corrected = filtrar_velocidad(speed_wind_corrected, video_label, TECHO_WIND_CORR),
    speed_current        = filtrar_velocidad(speed_current,        video_label, TECHO_CURRENT),
    speed_drone          = filtrar_velocidad(speed_drone,          video_label, TECHO_DRONE)
    # speed_wind_raw no se filtra (distribución limpia, máx 6.9 m/s)
  )

# 3c. Resumen del filtrado
cat("\n── Resumen tras filtrado de anomalías ──\n")
for (var in c("speed_wind_corrected", "speed_current", "speed_drone")) {
  x <- df[[var]]
  cat(sprintf("  %-22s  n_válidos=%-5d  media=%.4f  max=%.4f\n",
              var, sum(!is.na(x)), mean(x, na.rm=TRUE), max(x, na.rm=TRUE)))
}
cat("\n")

speed_vars <- c(
  "speed_wind_corrected",
  "speed_current",
  "speed_drone"
)

# ── 4. TESTS DE NORMALIDAD POR SESIÓN ────────────────────────────────────────
# Se aplican Shapiro-Wilk (n ≤ 5000) y Anderson-Darling
# Si una sesión tiene < 3 observaciones se omite

cat("\n", strrep("=", 70), "\n")
cat("  TEST DE NORMALIDAD POR SESIÓN\n")
cat(strrep("=", 70), "\n\n")

normality_results <- list()

for (var in speed_vars) {
  cat("Variable:", var, "\n", strrep("-", 50), "\n")
  res_list <- list()
  
  for (ses in levels(df$ID_label)) {
    x <- df %>% filter(ID_label == ses) %>% pull(.data[[var]])
    x <- x[!is.na(x)]
    n <- length(x)
    
    if (n < 3) {
      cat(sprintf("  %-8s: n=%d -> insuficiente\n", ses, n))
      next
    }
    
    # Shapiro-Wilk (máx 5000 obs)
    sw <- tryCatch(
      shapiro.test(if (n > 5000) sample(x, 5000) else x),
      error = function(e) list(statistic = NA, p.value = NA)
    )
    
    # Anderson-Darling
    ad <- tryCatch(
      nortest::ad.test(x),
      error = function(e) list(statistic = NA, p.value = NA)
    )
    
    normal_sw <- ifelse(!is.na(sw$p.value), ifelse(sw$p.value > 0.05, "✓", "✗"), "?")
    normal_ad <- ifelse(!is.na(ad$p.value), ifelse(ad$p.value > 0.05, "✓", "✗"), "?")
    
    cat(sprintf("  %-8s n=%-5d | SW: W=%.4f p=%.4f %s | AD: A=%.4f p=%.4f %s\n",
                ses, n,
                sw$statistic, sw$p.value, normal_sw,
                ad$statistic, ad$p.value, normal_ad))
    
    res_list[[ses]] <- data.frame(
      variable  = var,
      ID   = ses,
      n         = n,
      SW_W      = sw$statistic,
      SW_p      = sw$p.value,
      SW_normal = sw$p.value > 0.05,
      AD_A      = ad$statistic,
      AD_p      = ad$p.value,
      AD_normal = ad$p.value > 0.05
    )
  }
  normality_results[[var]] <- bind_rows(res_list)
  cat("\n")
}

normality_df <- bind_rows(normality_results)

# ── 5. TESTS DE HOMOCEDASTICIDAD (ENTRE SESIONES) ────────────────────────────
# Levene (robusto) y Bartlett (sensible a normalidad)

cat(strrep("=", 70), "\n")
cat("  TEST DE HOMOCEDASTICIDAD ENTRE SESIONES\n")
cat(strrep("=", 70), "\n\n")

homoscedasticity_results <- data.frame()

for (var in speed_vars) {
  sub <- df %>%
    select(ID_label, val = .data[[var]]) %>%
    filter(!is.na(val)) %>%
    filter(ID_label %in% (
      df %>% filter(!is.na(.data[[var]])) %>%
        count(ID_label) %>% filter(n >= 3) %>% pull(ID_label)
    ))
  
  if (n_distinct(sub$ID_label) < 2) {
    cat(var, ": menos de 2 sesiones con datos suficientes -> omitido\n\n")
    next
  }
  
  # Levene
  lev <- tryCatch(
    car::leveneTest(val ~ ID_label, data = sub),
    error = function(e) NULL
  )
  
  # Bartlett
  bar <- tryCatch(
    bartlett.test(val ~ ID_label, data = sub),
    error = function(e) NULL
  )
  
  lev_p <- if (!is.null(lev)) lev$`Pr(>F)`[1] else NA
  bar_p <- if (!is.null(bar)) bar$p.value      else NA
  
  cat(sprintf("%-25s | Levene: F=%.4f p=%.4f %s | Bartlett: K²=%.4f p=%.4f %s\n",
              var,
              if (!is.null(lev)) lev$`F value`[1] else NA, lev_p,
              ifelse(!is.na(lev_p), ifelse(lev_p > 0.05, "✓ homogéneo", "✗ heterogéneo"), "?"),
              if (!is.null(bar)) bar$statistic else NA, bar_p,
              ifelse(!is.na(bar_p), ifelse(bar_p > 0.05, "✓ homogéneo", "✗ heterogéneo"), "?")))
  
  homoscedasticity_results <- bind_rows(homoscedasticity_results, data.frame(
    variable      = var,
    Levene_F      = if (!is.null(lev)) lev$`F value`[1] else NA,
    Levene_p      = lev_p,
    Levene_homo   = if (!is.na(lev_p)) lev_p > 0.05 else NA,
    Bartlett_K2   = if (!is.null(bar)) bar$statistic else NA,
    Bartlett_p    = bar_p,
    Bartlett_homo = if (!is.na(bar_p)) bar_p > 0.05 else NA
  ))
}

cat("\n")

# ── TEMA BASE PARA PUBLICACIÓN ────────────────────────────────────────────────
#Por video
df_cor <- df %>% filter(!is.na(video_label))

#Por sesión
df_cor <- df %>% filter(!is.na(ID_label))

theme_pub <- function(base_size = 11) {
  theme_classic(base_size = base_size) %+replace%
    theme(
      # Ejes
      axis.line        = element_line(colour = "black", linewidth = 0.4),
      axis.ticks       = element_line(colour = "black", linewidth = 0.3),
      axis.ticks.length = unit(2.5, "pt"),
      axis.text        = element_text(colour = "black", size = rel(0.88)),
      axis.title       = element_text(colour = "black", size = rel(1.00)),
      # Facetas
      strip.background = element_rect(fill = "grey92", colour = NA),
      strip.text       = element_text(face = "bold", size = rel(0.95)),
      # Leyenda
      legend.key.size  = unit(10, "pt"),
      legend.text      = element_text(size = rel(0.85)),
      legend.title     = element_text(size = rel(0.90), face = "bold"),
      legend.background = element_blank(),
      legend.key       = element_blank(),
      # Títulos
      plot.title       = element_text(face = "bold", size = rel(1.10),
                                      hjust = 0, margin = margin(b = 4)),
      plot.subtitle    = element_text(size = rel(0.85), colour = "grey40",
                                      hjust = 0, margin = margin(b = 6)),
      plot.caption     = element_text(size = rel(0.75), colour = "grey50",
                                      hjust = 1),
      plot.margin      = margin(8, 10, 6, 8),
      # Panel
      panel.grid.major = element_line(colour = "grey90", linewidth = 0.25),
      panel.grid.minor = element_blank()
    )
}

# Paleta daltónica (Okabe-Ito) para vídeos – 8 colores distinguibles en B&W
okabe_8 <- c("#E69F00","#56B4E9","#009E73","#F0E442",
             "#0072B2","#D55E00","#CC79A7","#999999")

# Paleta para clases – ColorBrewer "Dark2" (imprime bien en escala de grises)
CLASES_NIVELES <- c("C_Shape", "L_Shape", "Upright", "Laid down", "Normal")

paleta_clases <- setNames(
  RColorBrewer::brewer.pal(length(CLASES_NIVELES), "Dark2"),
  CLASES_NIVELES
)

paleta_videos <- setNames(
  okabe_8[seq_len(n_distinct(df_cor$video_label))],
  sort(unique(df_cor$video_label))
)

# Paleta para sesiones
ID_NIVELES <- c("ID.1","ID.2","ID.3","ID.4","ID.5")
paleta_IDs <- setNames(okabe_8[seq_len(length(ID_NIVELES))],
                            ID_NIVELES)

# ── 6. GRÁFICA DE PROBABILIDAD DE CLASE ──────────────────────────────────────
df_clases <- df %>%
  filter(!is.na(video_label)) %>%
  mutate(Class = factor(as.character(.data[[class_col]]),
                        levels = CLASES_NIVELES)) %>%
  filter(!is.na(Class))

# 6a. Total global ─────────────────────────────────────────────────────────────
class_total <- df_clases %>%
  count(Class, .drop = FALSE) %>%
  mutate(prop = n / sum(n))

p_total <- ggplot(class_total,
                  aes(x = reorder(Class, -prop), y = prop, fill = Class)) +
  geom_col(colour = "grey20", width = 0.65, linewidth = 0.3) +
  geom_errorbar(aes(ymin = prop, ymax = prop), width = 0) +   # baseline
  geom_text(aes(label = sprintf("%d\n(%.1f%%)", n, prop * 100)),
            vjust = -0.35, size = 3.0, colour = "grey20") +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     expand = expansion(mult = c(0, 0.18))) +
  scale_fill_manual(values = paleta_clases, drop = FALSE) +
  labs(title    = "Dominant class distribution — overall",
       subtitle = sprintf("N = %d observations", sum(class_total$n)),
       x = NULL, y = "Relative frequency") +
  theme_pub(base_size = 12) +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 30, hjust = 1, size = rel(0.90)))

# 6b. Por vídeo ────────────────────────────────────────────────────────────────
class_video <- df_clases %>%
  group_by(video_label, Class, .drop = FALSE) %>%
  summarise(n = n(), .groups = "drop") %>%
  group_by(video_label) %>%
  mutate(prop = n / sum(n)) %>%
  ungroup() %>%
  filter(!is.na(video_label))

p_video <- ggplot(class_video,
                  aes(x = Class, y = prop, fill = Class)) +
  geom_col(colour = "grey20", width = 0.65, linewidth = 0.3) +
  geom_text(aes(label = ifelse(n > 0,
                               sprintf("%d\n(%.0f%%)", n, prop * 100), "")),
            vjust = -0.25, size = 2.4, colour = "grey20") +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     expand = expansion(mult = c(0, 0.22))) +
  scale_fill_manual(values = paleta_clases, drop = FALSE) +
  facet_wrap(~ video_label, ncol = 2) +
  labs(title = "Dominant class distribution by video",
       x = NULL, y = "Relative frequency") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 35, hjust = 1, size = rel(0.82)))

# 6b. Por sesión ────────────────────────────────────────────────────────────────
class_video <- df_clases %>%
  group_by(ID_label, Class, .drop = FALSE) %>%
  summarise(n = n(), .groups = "drop") %>%
  group_by(ID_label) %>%
  mutate(prop = n / sum(n)) %>%
  ungroup() %>%
  filter(!is.na(ID_label))

p_video <- ggplot(class_video,
                  aes(x = Class, y = prop, fill = Class)) +
  geom_col(colour = "grey20", width = 0.65, linewidth = 0.3) +
  geom_text(aes(label = ifelse(n > 0,
                               sprintf("%d\n(%.0f%%)", n, prop * 100), "")),
            vjust = -0.25, size = 2.4, colour = "grey20") +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                     expand = expansion(mult = c(0, 0.22))) +
  scale_fill_manual(values = paleta_videos, drop = FALSE) +
  facet_wrap(~ video, ncol = 2) +
  labs(title = "Dominant class distribution by video",
       x = NULL, y = "Relative frequency") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 35, hjust = 1, size = rel(0.82)))

# 6c. Heatmap ──────────────────────────────────────────────────────────────────
p_heat <- ggplot(class_video,
                 aes(x = ID_label, y = Class, fill = prop)) +
  geom_tile(colour = "white", linewidth = 0.7) +
  geom_text(aes(label = ifelse(n > 0,
                               sprintf("%.0f%%\n(n=%d)", prop * 100, n), "")),
            size = 2.8, colour = "grey10") +
  scale_fill_distiller(palette = "YlOrRd", direction = 1,
                       labels  = scales::percent_format(accuracy = 1),
                       na.value = "grey96",
                       name    = "Frequency") +
  scale_y_discrete(limits = rev(CLASES_NIVELES)) +
  labs(title = "Class frequency heatmap",
       x = "ID", y = NULL) +
  theme_pub(base_size = 11) +
  theme(axis.line  = element_blank(),
        axis.ticks = element_blank(),
        axis.text.x = element_text(angle = 30, hjust = 1),
        panel.grid  = element_blank())

# ── 7. BOXPLOTS DE VELOCIDADES POR VÍDEO ─────────────────────────────────────
df_long <- df %>%
  select(ID_label, all_of(speed_vars)) %>%
  pivot_longer(cols = all_of(speed_vars),
               names_to = "variable", values_to = "speed") %>%
  filter(!is.na(speed), !is.na(ID_label)) %>%
  mutate(variable = factor(variable,
                           levels = speed_vars,
                           labels = c("Corrected wind", "Current", "Drone")))

p_box <- ggplot(df_long,
                aes(x = ID_label, y = speed, fill = ID_label)) +
  geom_boxplot(outlier.shape = 1, outlier.size = 0.9,
               outlier.colour = "grey50",
               alpha = 0.75, linewidth = 0.35, na.rm = TRUE) +
  facet_wrap(~ variable, scales = "free_y", ncol = 1) +
  scale_fill_manual(values = paleta_IDs) +
  labs(title = "Speed distributions by ID",
       x = NULL, y = expression("Speed (m s"^{-1}*")")) +
  theme_pub(base_size = 11) +
  theme(legend.position = "none",
        axis.text.x     = element_text(angle = 35, hjust = 1))

# ── 8. GRÁFICAS DE CORRELACIÓN ───────────────────────────────────────────────
#Por video
df_cor <- df %>% filter(!is.na(video_label))

#Por sesión
df_cor <- df %>% filter(!is.na(ID_label))

cor_label <- function(x, y) {
  ok <- !is.na(x) & !is.na(y)
  if (sum(ok) < 5) return("n.d.")
  ct <- cor.test(x[ok], y[ok], method = "spearman")
  sprintf("\u03c1 = %.2f\np %s", ct$estimate,
          ifelse(ct$p.value < 0.001, "< 0.001",
                 paste0("= ", round(ct$p.value, 3))))
}

# ── 8a. Viento corregido ~ Dron ───────────────────────────────────────────────
df_wd <- df_cor %>% filter(!is.na(speed_wind_corrected), !is.na(speed_drone))

lab_wd <- df_wd %>%
  group_by(ID_label) %>%
  summarise(lbl  = cor_label(speed_wind_corrected, speed_drone),
            xpos = quantile(speed_wind_corrected, 0.97, na.rm = TRUE),
            ypos = max(speed_drone, na.rm = TRUE) * 0.95,
            .groups = "drop")

p_wd_global <- ggplot(df_wd,
                      aes(x = speed_wind_corrected, y = speed_drone,
                          colour = ID_label)) +
  geom_point(alpha = 0.40, size = 0.8, shape = 16) +
  geom_smooth(aes(group = 1), method = "lm", se = TRUE,
              colour = "black", fill = "grey80", linewidth = 0.7) +
  annotate("text", x = Inf, y = Inf,
           label = cor_label(df_wd$speed_wind_corrected, df_wd$speed_drone),
           hjust = 1.08, vjust = 1.4, size = 3.5, fontface = "bold") +
  scale_colour_manual(values = paleta_IDs, name = "ID") +
  labs(title = "Corrected wind speed vs. drone speed",
       x     = expression("Corrected wind speed (m s"^{-1}*")"),
       y     = expression("Drone speed (m s"^{-1}*")")) +
  theme_pub(base_size = 12) +
  guides(colour = guide_legend(override.aes = list(size = 2.5, alpha = 1)))

p_wd_video <- ggplot(df_wd,
                     aes(x = speed_wind_corrected, y = speed_drone,
                         colour = ID_label)) +
  geom_point(alpha = 0.45, size = 0.75, shape = 16) +
  geom_smooth(method = "lm", se = TRUE,
              linewidth = 0.65, fill = "grey85") +
  geom_text(data = lab_wd, aes(x = xpos, y = ypos, label = lbl),
            inherit.aes = FALSE, size = 2.8, hjust = 1,
            lineheight = 1.1, fontface = "italic") +
  scale_colour_manual(values = paleta_IDs) +
  facet_wrap(~ ID_label, scales = "free") +
  labs(title = "Corrected wind speed vs. drone speed — by ID",
       x     = expression("Corrected wind speed (m s"^{-1}*")"),
       y     = expression("Drone speed (m s"^{-1}*")")) +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")

# ── 8b. Corriente ~ Dron ──────────────────────────────────────────────────────
df_cd <- df_cor %>% filter(!is.na(speed_current), !is.na(speed_drone))

lab_cd <- df_cd %>%
  group_by(ID_label) %>%
  summarise(lbl  = cor_label(speed_current, speed_drone),
            xpos = quantile(speed_current, 0.97, na.rm = TRUE),
            ypos = max(speed_drone, na.rm = TRUE) * 0.95,
            .groups = "drop")

p_cd_global <- ggplot(df_cd,
                      aes(x = speed_current, y = speed_drone,
                          colour = ID_label)) +
  geom_point(alpha = 0.40, size = 0.8, shape = 16) +
  geom_smooth(aes(group = 1), method = "lm", se = TRUE,
              colour = "black", fill = "grey80", linewidth = 0.7) +
  annotate("text", x = Inf, y = Inf,
           label = cor_label(df_cd$speed_current, df_cd$speed_drone),
           hjust = 1.08, vjust = 1.4, size = 3.5, fontface = "bold") +
  scale_colour_manual(values = paleta_IDs, name = "ID") +
  labs(title = "Current speed vs. drone speed",
       x     = expression("Current speed (m s"^{-1}*")"),
       y     = expression("Drone speed (m s"^{-1}*")")) +
  theme_pub(base_size = 12) +
  guides(colour = guide_legend(override.aes = list(size = 2.5, alpha = 1)))

p_cd_video <- ggplot(df_cd,
                     aes(x = speed_current, y = speed_drone,
                         colour = ID_label)) +
  geom_point(alpha = 0.45, size = 0.75, shape = 16) +
  geom_smooth(method = "lm", se = TRUE,
              linewidth = 0.65, fill = "grey85") +
  geom_text(data = lab_cd, aes(x = xpos, y = ypos, label = lbl),
            inherit.aes = FALSE, size = 2.8, hjust = 1,
            lineheight = 1.1, fontface = "italic") +
  scale_colour_manual(values = paleta_IDs) +
  facet_wrap(~ ID_label, scales = "free") +
  labs(title = "Current speed vs. drone speed — by ID",
       x     = expression("Current speed (m s"^{-1}*")"),
       y     = expression("Drone speed (m s"^{-1}*")")) +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")

# ── 8c. Clase ~ Viento ────────────────────────────────────────────────────────
df_cw <- df_cor %>%
  filter(!is.na(speed_wind_corrected)) %>%
  mutate(Class = factor(as.character(.data[[class_col]]),
                        levels = CLASES_NIVELES)) %>%
  filter(!is.na(Class))

kw_wind     <- kruskal.test(speed_wind_corrected ~ Class, data = df_cw)
kw_wind_lbl <- sprintf("Kruskal–Wallis: \u03c7\u00b2 = %.2f, df = %d, p %s",
                       kw_wind$statistic, kw_wind$parameter,
                       ifelse(kw_wind$p.value < 0.001, "< 0.001",
                              paste0("= ", round(kw_wind$p.value, 3))))

p_class_wind <- ggplot(df_cw,
                       aes(x = Class, y = speed_wind_corrected, fill = Class)) +
  geom_violin(alpha = 0.45, trim = TRUE, colour = NA, linewidth = 0) +
  geom_boxplot(width = 0.16, outlier.shape = 1, outlier.size = 0.7,
               alpha = 0.90, linewidth = 0.35, colour = "grey20") +
  stat_summary(fun = mean, geom = "point", shape = 18,
               size = 2.2, colour = "white") +
  scale_fill_manual(values = paleta_clases, drop = FALSE) +
  facet_wrap(~ video_label, scales = "free_y", ncol = 2) +
  labs(title    = "Corrected wind speed by dominant class",
       subtitle = kw_wind_lbl,
       x = NULL,
       y = expression("Corrected wind speed (m s"^{-1}*")")) +
  theme_pub(base_size = 10) +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 35, hjust = 1))

# ── 8d. Clase ~ Corriente ─────────────────────────────────────────────────────
df_cc <- df_cor %>%
  filter(!is.na(speed_current)) %>%
  mutate(Class = factor(as.character(.data[[class_col]]),
                        levels = CLASES_NIVELES)) %>%
  filter(!is.na(Class))

kw_curr     <- kruskal.test(speed_current ~ Class, data = df_cc)
kw_curr_lbl <- sprintf("Kruskal–Wallis: \u03c7\u00b2 = %.2f, df = %d, p %s",
                       kw_curr$statistic, kw_curr$parameter,
                       ifelse(kw_curr$p.value < 0.001, "< 0.001",
                              paste0("= ", round(kw_curr$p.value, 3))))

p_class_curr <- ggplot(df_cc,
                       aes(x = Class, y = speed_current, fill = Class)) +
  geom_violin(alpha = 0.45, trim = TRUE, colour = NA, linewidth = 0) +
  geom_boxplot(width = 0.16, outlier.shape = 1, outlier.size = 0.7,
               alpha = 0.90, linewidth = 0.35, colour = "grey20") +
  stat_summary(fun = mean, geom = "point", shape = 18,
               size = 2.2, colour = "white") +
  scale_fill_manual(values = paleta_clases, drop = FALSE) +
  facet_wrap(~ video_label, scales = "free_y", ncol = 2) +
  labs(title    = "Current speed by dominant class",
       subtitle = kw_curr_lbl,
       x = NULL,
       y = expression("Current speed (m s"^{-1}*")")) +
  theme_pub(base_size = 10) +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 35, hjust = 1))

# ── 8e. CORRELACIÓN DE ÁNGULOS ────────────────────────────────────────────────
# ── Helper: correlación circular de Jammalamadaka-Sarma ──────────────────────
# Devuelve lista con r (coeficiente), estadístico T y p-valor (aprox. normal)
circ_cor_js <- function(alpha, beta) {
  ok <- !is.na(alpha) & !is.na(beta)
  if (sum(ok) < 5) return(list(r = NA_real_, T_stat = NA_real_, p = NA_real_))
  
  a <- circular::circular(alpha[ok] * pi / 180,
                          type = "angles", units = "radians", modulo = "2pi")
  b <- circular::circular(beta[ok]  * pi / 180,
                          type = "angles", units = "radians", modulo = "2pi")
  
  # Sin test=TRUE para obtener el coeficiente, luego test separado para p-valor
  r_val  <- tryCatch(as.numeric(circular::cor.circular(a, b)),
                     error = function(e) NA_real_)
  
  ht     <- tryCatch(circular::cor.circular(a, b, test = TRUE),
                     error = function(e) NULL)
  
  T_val  <- if (!is.null(ht)) as.numeric(ht$statistic) else NA_real_
  p_val  <- if (!is.null(ht)) as.numeric(ht$p.value)   else NA_real_
  
  list(r = r_val, T_stat = T_val, p = p_val)
}

# Helper de etiqueta para gráficas
cor_label_circ <- function(alpha, beta) {
  ok <- !is.na(alpha) & !is.na(beta)
  if (sum(ok) < 5) return("n.d.")
  res <- circ_cor_js(alpha[ok], beta[ok])
  sprintf("r\u1d9c = %.2f\np %s",
          res$r,
          ifelse(res$p < 0.001, "< 0.001",
                 paste0("= ", round(res$p, 3))))
}

df <- df %>%
  mutate(
    angle_wind_corrected = (atan2(u_wind_corrected, v_wind_corrected) * 180 / pi) %% 360,
    angle_drone          = (atan2(u_drone,          v_drone)          * 180 / pi) %% 360,
    delta_angle          = ((angle_wind_corrected - angle_drone) + 180) %% 360 - 180
  )

df_ang <- df %>%
  filter(!is.na(video_label),
         !is.na(angle_wind_corrected), !is.na(angle_drone),
         !is.na(speed_wind_corrected), !is.na(speed_drone),
         speed_wind_corrected > 0, speed_drone > 0)

cat("\n", strrep("=", 70), "\n")
cat("  CORRELACIÓN CIRCULAR (Jammalamadaka-Sarma): Viento ~ Dron\n")
cat(strrep("=", 70), "\n\n")
cat("Filas usadas (ángulos válidos):", nrow(df_ang), "\n\n")

# ── Test global ───────────────────────────────────────────────────────────────
js_global<- circ_cor_js(df_ang$angle_wind_corrected,
                              df_ang$angle_drone)

cat(sprintf("Global  r_c = %.4f  T = %.4f  p %s\n",
            js_global$r,
            js_global$T_stat,
            ifelse(js_global$p < 0.001, "< 0.001",
                   paste0("= ", round(js_global$p, 4)))))

# ── Tests por vídeo ───────────────────────────────────────────────────────────
cat("\nPor vídeo:\n")
ang_video_stats <- df_ang %>%
  group_by(video_label) %>%
  summarise(
    n          = n(),
    .circ      = list(
      if (n() >= 5)
        circ_cor_js(angle_wind_corrected, angle_drone)
      else
        list(r = NA_real_, T_stat = NA_real_, p = NA_real_)
    ),
    mean_delta = mean(delta_angle, na.rm = TRUE),
    sd_delta   = sd(delta_angle,   na.rm = TRUE),
    .groups    = "drop"
  ) %>%
  mutate(
    r_c    = sapply(.circ, `[[`, "r"),
    T_stat = sapply(.circ, `[[`, "T_stat"),
    p_val  = sapply(.circ, `[[`, "p")
  ) %>%
  select(-".circ")
print(ang_video_stats)

# ── Tests por sesión (ID_label) ───────────────────────────────────────────────
cat("\nPor sesión:\n")
ang_ID_stats <- df_ang %>%
  group_by(ID_label) %>%
  summarise(
    n          = n(),
    .circ      = list(
      if (n() >= 5)
        circ_cor_js(angle_wind_corrected, angle_drone)
      else
        list(r = NA_real_, T_stat = NA_real_, p = NA_real_)
    ),
    mean_delta = mean(delta_angle, na.rm = TRUE),
    sd_delta   = sd(delta_angle,   na.rm = TRUE),
    .groups    = "drop"
  ) %>%
  mutate(
    r_c    = sapply(.circ, `[[`, "r"),
    T_stat = sapply(.circ, `[[`, "T_stat"),
    p_val  = sapply(.circ, `[[`, "p")
  ) %>%
  select(-".circ")
print(ang_ID_stats)

# ── Etiqueta global para gráfica ──────────────────────────────────────────────
lbl_global_ang <- if (!is.na(js_global$r)) {
  sprintf("r\u1d9c = %.2f\np %s",
          js_global$r,
          ifelse(js_global$p < 0.001, "< 0.001",
                 paste0("= ", round(js_global$p, 3))))
} else {
  "n.d."
}

# ── 8e-iii. Scatter global ────────────────────────────────────────────────────
ann_global <- data.frame(
  x     = Inf,
  y     = -Inf,
  label = lbl_global_ang
)

p_ang_global <- ggplot(df_ang,
                       aes(x = angle_wind_corrected, y = angle_drone,
                           colour = ID_label)) +
  geom_abline(slope = 1, intercept = 0,
              linetype = "dashed", colour = "grey60", linewidth = 0.5) +
  geom_point(alpha = 0.35, size = 0.8, shape = 16) +
  geom_smooth(aes(group = 1), method = "lm", se = TRUE,
              colour = "black", fill = "grey80", linewidth = 0.7) +
  geom_text(data = ann_global,
            aes(x = x, y = y, label = label),
            inherit.aes = FALSE,
            hjust = 1.05, vjust = -0.4,
            size = 3.5, fontface = "bold", lineheight = 1.2) +
  scale_colour_manual(values = paleta_video, name = "Video") +
  scale_x_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°"),
                     limits = c(0, 360)) +
  scale_y_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°"),
                     limits = c(0, 360)) +
  coord_fixed() +
  labs(title    = "Wind direction vs. drone direction",
       subtitle = "Jammalamadaka\u2013Sarma circular correlation",
       x = "Corrected wind direction (°, going-to)",
       y = "Drone direction (°, going-to)") +
  theme_pub(base_size = 12) +
  guides(colour = guide_legend(override.aes = list(size = 2.5, alpha = 1)))

# ── 8e-iv. Scatter por vídeo ─paleta_videos# ── 8e-iv. Scatter por vídeo ──────────────────────────────────────────────────
lab_ang_vid <- ang_video_stats %>%
  mutate(lbl = ifelse(!is.na(r_c),
                      sprintf("r\u1d9c = %.2f\np %s", r_c,
                              ifelse(p_val < 0.001, "< 0.001",
                                     paste0("= ", round(p_val, 3)))),
                      "n.d."))

p_ang_video <- ggplot(df_ang,
                      aes(x = angle_wind_corrected, y = angle_drone,
                          colour = video_label)) +
  geom_abline(slope = 1, intercept = 0,
              linetype = "dashed", colour = "grey65", linewidth = 0.45) +
  geom_point(alpha = 0.40, size = 0.75, shape = 16) +
  geom_smooth(method = "lm", se = TRUE,
              linewidth = 0.65, fill = "grey85") +
  geom_text(data = lab_ang_vid,
            aes(x = Inf, y = -Inf, label = lbl),
            inherit.aes = FALSE, hjust = 1.05, vjust = -0.4,
            size = 2.8, fontface = "italic", lineheight = 1.1) +
  scale_colour_manual(values = paleta_videos) +
  scale_x_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°")) +
  scale_y_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°")) +
  facet_wrap(~ video_label, scales = "free") +
  labs(title    = "Wind direction vs. drone direction — by video",
       subtitle = "Jammalamadaka\u2013Sarma circular correlation",
       x = "Corrected wind direction (°)",
       y = "Drone direction (°)") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")

# ── Etiquetas por sesión para gráficas ───────────────────────────────────────
lab_ang_ID <- ang_ID_stats %>%
  mutate(lbl = ifelse(!is.na(r_c),
                      sprintf("r\u1d9c = %.2f\np %s", r_c,
                              ifelse(p_val < 0.001, "< 0.001",
                                     paste0("= ", round(p_val, 3)))),
                      "n.d."))

p_ang_session <- ggplot(df_ang,
                      aes(x = angle_wind_corrected, y = angle_drone,
                          colour = ID_label)) +
  geom_abline(slope = 1, intercept = 0,
              linetype = "dashed", colour = "grey65", linewidth = 0.45) +
  geom_point(alpha = 0.40, size = 0.75, shape = 16) +
  geom_smooth(method = "lm", se = TRUE,
              linewidth = 0.65, fill = "grey85") +
  geom_text(data = lab_ang_ID,
            aes(x = Inf, y = -Inf, label = lbl),
            inherit.aes = FALSE, hjust = 1.05, vjust = -0.4,
            size = 2.8, fontface = "italic", lineheight = 1.1) +
  scale_colour_manual(values = paleta_IDs) +
  scale_x_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°")) +
  scale_y_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°")) +
  facet_wrap(~ ID_label, scales = "free") +
  labs(title    = "Wind direction vs. drone direction — by video",
       subtitle = "Jammalamadaka\u2013Sarma circular correlation",
       x = "Corrected wind direction (°)",
       y = "Drone direction (°)") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")
p_ang_session
# ── 8e-v. Histograma diferencia circular ─────────────────────────────────────
p_delta <- ggplot(df_ang, aes(x = delta_angle, fill = video_label)) +
  geom_histogram(binwidth = 15, colour = "grey20", linewidth = 0.25,
                 alpha = 0.80, position = "identity") +
  geom_vline(xintercept = 0, colour = "black",
             linetype = "dashed", linewidth = 0.6) +
  scale_fill_manual(values = paleta_videos) +
  scale_x_continuous(breaks = seq(-180, 180, 60),
                     labels = c("-180°","-120°","-60°","0°",
                                "60°","120°","180°")) +
  facet_wrap(~ video_label, scales = "free_y", ncol = 2) +
  labs(title    = "Angular difference: wind direction \u2212 drone direction",
       subtitle = "Dashed line at 0\u00b0 = same direction  |  \u00b1180\u00b0 = opposing",
       x = "Angular difference (°)", y = "Count") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")

# ── 8e. SESION ANALISIS ──────────────────────────────
# ── Tests por sesión ──────────────────────────────────────────────────────────
cat("\nPor sesión:\n")
ang_video_stats <- df_ang %>%
  group_by(ID_label) %>%
  summarise(
    n      = n(),
    .circ  = list(
      if (n() >= 5)
        circ_cor_js(angle_wind_corrected, angle_drone)
      else
        list(r = NA_real_, T_stat = NA_real_, p = NA_real_)
    ),
    mean_delta = mean(delta_angle, na.rm = TRUE),
    sd_delta   = sd(delta_angle,   na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(
    r_c    = sapply(.circ, `[[`, "r"),
    T_stat = sapply(.circ, `[[`, "T_stat"),
    p_val  = sapply(.circ, `[[`, "p")
  ) %>%
  select(-".circ")
print(ang_video_stats)

# ── Scatter global ────────────────────────────────────────────────────────────
p_ang_global <- ggplot(df_ang,
                       aes(x = angle_wind_corrected, y = angle_drone,
                           colour = ID_label)) +
  geom_abline(slope = 1, intercept = 0,
              linetype = "dashed", colour = "grey60", linewidth = 0.5) +
  geom_point(alpha = 0.35, size = 0.8, shape = 16) +
  geom_smooth(aes(group = 1), method = "lm", se = TRUE,
              colour = "black", fill = "grey80", linewidth = 0.7) +
  geom_text(data = ann_global,
            aes(x = x, y = y, label = label),
            inherit.aes = FALSE,
            hjust = 1.05, vjust = -0.4,
            size = 3.5, fontface = "bold", lineheight = 1.2) +
  scale_colour_manual(values = paleta_IDs, name = "ID") +
  scale_x_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°"),
                     limits = c(0, 360)) +
  scale_y_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°"),
                     limits = c(0, 360)) +
  coord_fixed() +
  labs(title    = "Wind direction vs. drone direction",
       subtitle = "Jammalamadaka\u2013Sarma circular correlation",
       x = "Corrected wind direction (°, going-to)",
       y = "Drone direction (°, going-to)") +
  theme_pub(base_size = 12) +
  guides(colour = guide_legend(override.aes = list(size = 2.5, alpha = 1)))

# ── Scatter por sesión ────────────────────────────────────────────────────────
lab_ang_vid <- ang_video_stats %>%
  mutate(lbl = ifelse(!is.na(r_c),
                      sprintf("r\u1d9c = %.2f\np %s", r_c,
                              ifelse(p_val < 0.001, "< 0.001",
                                     paste0("= ", round(p_val, 3)))),
                      "n.d."))

p_ang_video <- ggplot(df_ang,
                      aes(x = angle_wind_corrected, y = angle_drone,
                          colour = ID_label)) +
  geom_abline(slope = 1, intercept = 0,
              linetype = "dashed", colour = "grey65", linewidth = 0.45) +
  geom_point(alpha = 0.40, size = 0.75, shape = 16) +
  geom_smooth(method = "lm", se = TRUE,
              linewidth = 0.65, fill = "grey85") +
  geom_text(data = lab_ang_vid,
            aes(x = Inf, y = -Inf, label = lbl),
            inherit.aes = FALSE, hjust = 1.05, vjust = -0.4,
            size = 2.8, fontface = "italic", lineheight = 1.1) +
  scale_colour_manual(values = paleta_IDs) +
  scale_x_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°")) +
  scale_y_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°")) +
  facet_wrap(~ ID_label, scales = "free") +
  labs(title    = "Wind direction vs. drone direction — by ID",
       subtitle = "Jammalamadaka\u2013Sarma circular correlation",
       x = "Corrected wind direction (°)",
       y = "Drone direction (°)") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")

# ── Histograma diferencia circular ────────────────────────────────────────────
p_delta <- ggplot(df_ang, aes(x = delta_angle, fill = ID_label)) +
  geom_histogram(binwidth = 15, colour = "grey20", linewidth = 0.25,
                 alpha = 0.80, position = "identity") +
  geom_vline(xintercept = 0, colour = "black",
             linetype = "dashed", linewidth = 0.6) +
  scale_fill_manual(values = paleta_IDs) +
  scale_x_continuous(breaks = seq(-180, 180, 60),
                     labels = c("-180°","-120°","-60°","0°",
                                "60°","120°","180°")) +
  facet_wrap(~ ID_label, scales = "free_y", ncol = 2) +
  labs(title    = "Angular difference: wind direction \u2212 drone direction",
       subtitle = "Dashed line at 0\u00b0 = same direction  |  \u00b1180\u00b0 = opposing",
       x = "Angular difference (°)", y = "Count") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")

# ── 8f. ANÁLISIS DE DIFERENCIA ANGULAR ABSOLUTA ──────────────────────────────

df <- df %>%
  mutate(abs_delta_angle = abs(delta_angle))

df_ang <- df_ang %>%
  mutate(abs_delta_angle = abs(delta_angle))

# ── 8f-i. Resumen estadístico por vídeo ──────────────────────────────────────
cat("\n", strrep("=", 70), "\n")
cat("  DIFERENCIA ANGULAR ABSOLUTA |wind - drone| POR VÍDEO\n")
cat(strrep("=", 70), "\n\n")

abs_delta_stats <- df_ang %>%
  group_by(video_label) %>%
  summarise(
    n              = n(),
    mean_abs       = mean(abs_delta_angle,   na.rm = TRUE),
    sd_abs         = sd(abs_delta_angle,     na.rm = TRUE),
    median_abs     = median(abs_delta_angle, na.rm = TRUE),
    q25            = quantile(abs_delta_angle, 0.25, na.rm = TRUE),
    q75            = quantile(abs_delta_angle, 0.75, na.rm = TRUE),
    pct_below_45   = mean(abs_delta_angle <  45, na.rm = TRUE) * 100,
    pct_below_90   = mean(abs_delta_angle <  90, na.rm = TRUE) * 100,
    .groups = "drop"
  )

print(abs_delta_stats)

# ── Resumen estadístico por sesión ─────────────────────────────────────
abs_delta_stats <- df_ang %>%
  group_by(ID_label) %>%
  summarise(
    n            = n(),
    mean_abs     = mean(abs_delta_angle,   na.rm = TRUE),
    sd_abs       = sd(abs_delta_angle,     na.rm = TRUE),
    median_abs   = median(abs_delta_angle, na.rm = TRUE),
    q25          = quantile(abs_delta_angle, 0.25, na.rm = TRUE),
    q75          = quantile(abs_delta_angle, 0.75, na.rm = TRUE),
    pct_below_45 = mean(abs_delta_angle <  45, na.rm = TRUE) * 100,
    pct_below_90 = mean(abs_delta_angle <  90, na.rm = TRUE) * 100,
    .groups = "drop"
  )
print(abs_delta_stats)

# ── 8f-ii. Test de normalidad sobre abs_delta_angle ──────────────────────────
cat("\nTests de normalidad (Shapiro-Wilk + Anderson-Darling):\n")
cat(strrep("-", 50), "\n")

for (vid in sort(unique(df_ang$video_label))) {
  x <- df_ang %>% filter(video_label == vid) %>% pull(abs_delta_angle)
  x <- x[!is.na(x)]
  n <- length(x)
  if (n < 3) { cat(sprintf("  %-12s n=%d -> insuficiente\n", vid, n)); next }
  
  sw <- tryCatch(shapiro.test(if (n > 5000) sample(x, 5000) else x),
                 error = function(e) list(statistic = NA, p.value = NA))
  ad <- tryCatch(nortest::ad.test(x),
                 error = function(e) list(statistic = NA, p.value = NA))
  
  cat(sprintf("  %-12s n=%-5d | SW: W=%.4f p=%.4f %s | AD: A=%.4f p=%.4f %s\n",
              vid, n,
              sw$statistic, sw$p.value,
              ifelse(!is.na(sw$p.value), ifelse(sw$p.value > 0.05, "✓", "✗"), "?"),
              ad$statistic, ad$p.value,
              ifelse(!is.na(ad$p.value), ifelse(ad$p.value > 0.05, "✓", "✗"), "?")))
}

# ── Test de normalidad sobre abs_delta_angle por sesión ─────────────────────────────────────
cat("\nTests de normalidad (Shapiro-Wilk + Anderson-Darling):\n")
cat(strrep("-", 50), "\n")

for (ses in levels(df_ang$ID_label)) {
  x <- df_ang %>% filter(ID_label == ses) %>% pull(abs_delta_angle)
  x <- x[!is.na(x)]
  n <- length(x)
  if (n < 3) { cat(sprintf("  %-8s n=%d -> insuficiente\n", ses, n)); next }
  
  sw <- tryCatch(shapiro.test(if (n > 5000) sample(x, 5000) else x),
                 error = function(e) list(statistic = NA, p.value = NA))
  ad <- tryCatch(nortest::ad.test(x),
                 error = function(e) list(statistic = NA, p.value = NA))
  
  cat(sprintf("  %-8s n=%-5d | SW: W=%.4f p=%.4f %s | AD: A=%.4f p=%.4f %s\n",
              ses, n,
              sw$statistic, sw$p.value,
              ifelse(!is.na(sw$p.value), ifelse(sw$p.value > 0.05, "✓", "✗"), "?"),
              ad$statistic, ad$p.value,
              ifelse(!is.na(ad$p.value), ifelse(ad$p.value > 0.05, "✓", "✗"), "?")))
}

# ── 8f-iii. Kruskal-Wallis entre vídeos ──────────────────────────────────────
cat("\n")
kw_abs <- kruskal.test(abs_delta_angle ~ video_label, data = df_ang)
cat(sprintf("Kruskal-Wallis entre vídeos: chi² = %.4f  df = %d  p %s\n",
            kw_abs$statistic, kw_abs$parameter,
            ifelse(kw_abs$p.value < 0.001, "< 0.001",
                   paste0("= ", round(kw_abs$p.value, 4)))))

# ── Kruskal-Wallis entre vídeos ──────────────────────────────────────
kw_abs <- kruskal.test(abs_delta_angle ~ ID_label, data = df_ang)
cat(sprintf("Kruskal-Wallis entre sesiones: chi² = %.4f  df = %d  p %s\n",
            kw_abs$statistic, kw_abs$parameter,
            ifelse(kw_abs$p.value < 0.001, "< 0.001",
                   paste0("= ", round(kw_abs$p.value, 4)))))

# ── 8f-iv. Post-hoc: Dunn test con corrección de Benjamini-Hochberg ──────────
if (!requireNamespace("dunn.test", quietly = TRUE)) install.packages("dunn.test")
library(dunn.test)

cat("\nDunn post-hoc (BH correction):\n")
cat(strrep("-", 50), "\n")
dunn_abs <- dunn.test::dunn.test(df_ang$abs_delta_angle,
                                 df_ang$video_label,
                                 method = "bh", altp = TRUE)

# ── Post-hoc: Dunn test con corrección de Benjamini-Hochberg entre sesiones──────────
cat("\nDunn post-hoc (BH correction):\n")
cat(strrep("-", 50), "\n")
dunn_abs <- dunn.test::dunn.test(df_ang$abs_delta_angle,
                                 df_ang$ID_label,
                                 method = "bh", altp = TRUE)

# ── 8f-v. Boxplot abs_delta_angle por vídeo ───────────────────────────────────
kw_abs_lbl <- sprintf("Kruskal\u2013Wallis: \u03c7\u00b2 = %.2f, df = %d, p %s",
                      kw_abs$statistic, kw_abs$parameter,
                      ifelse(kw_abs$p.value < 0.001, "< 0.001",
                             paste0("= ", round(kw_abs$p.value, 3))))

p_abs_box <- ggplot(df_ang,
                    aes(x = video_label, y = abs_delta_angle,
                        fill = video_label)) +
  geom_boxplot(outlier.shape = 1, outlier.size = 0.9,
               outlier.colour = "grey50",
               alpha = 0.75, linewidth = 0.35) +
  geom_hline(yintercept = c(45, 90),
             linetype = "dashed", colour = "grey40", linewidth = 0.4) +
  annotate("text", x = 0.55, y = 46, label = "45°",
           size = 3, colour = "grey40", vjust = -0.3) +
  annotate("text", x = 0.55, y = 91, label = "90°",
           size = 3, colour = "grey40", vjust = -0.3) +
  scale_fill_manual(values = paleta_videos) +
  scale_y_continuous(breaks = seq(0, 180, 30),
                     labels = paste0(seq(0, 180, 30), "°"),
                     limits = c(0, 185)) +
  labs(title    = "Absolute angular difference |wind \u2212 drone| by video",
       subtitle = kw_abs_lbl,
       x = NULL,
       y = "|\u0394\u03b8| (°)") +
  theme_pub(base_size = 12) +
  theme(legend.position = "none",
        axis.text.x     = element_text(angle = 30, hjust = 1))

# ── Boxplot abs_delta_angle por sesion ───────────────────────────────────
kw_abs_lbl <- sprintf("Kruskal\u2013Wallis: \u03c7\u00b2 = %.2f, df = %d, p %s",
                      kw_abs$statistic, kw_abs$parameter,
                      ifelse(kw_abs$p.value < 0.001, "< 0.001",
                             paste0("= ", round(kw_abs$p.value, 3))))

p_abs_box <- ggplot(df_ang,
                    aes(x = ID_label, y = abs_delta_angle,
                        fill = ID_label)) +
  geom_boxplot(outlier.shape = 1, outlier.size = 0.9,
               outlier.colour = "grey50",
               alpha = 0.75, linewidth = 0.35) +
  geom_hline(yintercept = c(45, 90),
             linetype = "dashed", colour = "grey40", linewidth = 0.4) +
  annotate("text", x = 0.55, y = 46, label = "45°",
           size = 3, colour = "grey40", vjust = -0.3) +
  annotate("text", x = 0.55, y = 91, label = "90°",
           size = 3, colour = "grey40", vjust = -0.3) +
  scale_fill_manual(values = paleta_IDs) +
  scale_y_continuous(breaks = seq(0, 180, 30),
                     labels = paste0(seq(0, 180, 30), "°"),
                     limits = c(0, 185)) +
  labs(title    = "Absolute angular difference |wind \u2212 drone| by ID",
       subtitle = kw_abs_lbl,
       x = NULL,
       y = "|\u0394\u03b8| (°)") +
  theme_pub(base_size = 12) +
  theme(legend.position = "none",
        axis.text.x     = element_text(angle = 30, hjust = 1))

# ── 8f-vi. Histograma abs_delta_angle por vídeo ───────────────────────────────
p_abs_hist <- ggplot(df_ang,
                     aes(x = abs_delta_angle, fill = video_label)) +
  geom_histogram(binwidth = 10, colour = "grey20",
                 linewidth = 0.25, alpha = 0.80) +
  geom_vline(xintercept = c(45, 90),
             linetype = "dashed", colour = "grey30", linewidth = 0.5) +
  scale_fill_manual(values = paleta_videos) +
  scale_x_continuous(breaks = seq(0, 180, 30),
                     labels = paste0(seq(0, 180, 30), "°"),
                     limits = c(0, 180)) +
  facet_wrap(~ video_label, scales = "free_y", ncol = 2) +
  labs(title    = "Distribution of |wind \u2212 drone| angular difference",
       subtitle = "Dashed lines at 45° and 90°",
       x = "|\u0394\u03b8| (°)", y = "Count") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")

# ── Histograma abs_delta_angle por sesion ───────────────────────────────
p_abs_hist <- ggplot(df_ang,
                     aes(x = abs_delta_angle, fill = ID_label)) +
  geom_histogram(binwidth = 10, colour = "grey20",
                 linewidth = 0.25, alpha = 0.80) +
  geom_vline(xintercept = c(45, 90),
             linetype = "dashed", colour = "grey30", linewidth = 0.5) +
  scale_fill_manual(values = paleta_IDs) +
  scale_x_continuous(breaks = seq(0, 180, 30),
                     labels = paste0(seq(0, 180, 30), "°"),
                     limits = c(0, 180)) +
  facet_wrap(~ ID_label, scales = "free_y", ncol = 2) +
  labs(title    = "Distribution of |wind \u2212 drone| angular difference",
       subtitle = "Dashed lines at 45° and 90°",
       x = "|\u0394\u03b8| (°)", y = "Count") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")

# ── 8f-vii. Densidad acumulada (ECDF) por vídeo ───────────────────────────────
p_abs_ecdf <- ggplot(df_ang,
                     aes(x = abs_delta_angle, colour = video_label)) +
  stat_ecdf(linewidth = 0.7) +
  geom_vline(xintercept = c(45, 90),
             linetype = "dashed", colour = "grey40", linewidth = 0.4) +
  scale_colour_manual(values = paleta_videos, name = "Video") +
  scale_x_continuous(breaks = seq(0, 180, 30),
                     labels = paste0(seq(0, 180, 30), "°"),
                     limits = c(0, 180)) +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(title    = "Cumulative distribution of |\u0394\u03b8|",
       subtitle = "Proportion of observations below each angular threshold",
       x = "|\u0394\u03b8| (°)", y = "Cumulative frequency") +
  theme_pub(base_size = 12) +
  guides(colour = guide_legend(override.aes = list(linewidth = 1.5)))

# ── Densidad acumulada (ECDF) por vídeo ───────────────────────────────
p_abs_ecdf <- ggplot(df_ang,
                     aes(x = abs_delta_angle, colour = ID_label)) +
  stat_ecdf(linewidth = 0.7) +
  geom_vline(xintercept = c(45, 90),
             linetype = "dashed", colour = "grey40", linewidth = 0.4) +
  scale_colour_manual(values = paleta_IDs, name = "ID") +
  scale_x_continuous(breaks = seq(0, 180, 30),
                     labels = paste0(seq(0, 180, 30), "°"),
                     limits = c(0, 180)) +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(title    = "Cumulative distribution of |\u0394\u03b8|",
       subtitle = "Proportion of observations below each angular threshold",
       x = "|\u0394\u03b8| (°)", y = "Cumulative frequency") +
  theme_pub(base_size = 12) +
  guides(colour = guide_legend(override.aes = list(linewidth = 1.5)))

# ── 8g. POLAR PLOT: CLASE × VELOCIDAD VIENTO × ÁNGULO DRON ───────────────────

# Preparar datos: ángulo de movimiento del dron (going-to) y velocidad del viento
df_polar <- df %>%
  filter(!is.na(video_label),
         !is.na(speed_wind_corrected),
         !is.na(speed_drone),
         !is.na(angle_drone),
         speed_drone > 0,
         speed_wind_corrected > 0) %>%
  mutate(
    Class = factor(as.character(.data[[class_col]]),
                   levels = CLASES_NIVELES)
  ) %>%
  filter(!is.na(Class))

# ── 8g-i. Polar global: todos los vídeos, coloreado por clase ─────────────────
p_polar_class <- ggplot(df_polar,
                        aes(x     = angle_drone,
                            y     = speed_wind_corrected,
                            colour = Class)) +
  geom_point(alpha = 0.45, size = 0.9, shape = 16) +
  # Media por clase como punto grande
  stat_summary_bin(
    aes(x = angle_drone, y = speed_wind_corrected, colour = Class),
    fun     = "mean",
    geom    = "point",
    size    = 3.5,
    shape   = 18,
    binwidth = 30
  ) +
  scale_x_continuous(
    limits = c(0, 360),
    breaks = seq(0, 315, 45),
    labels = c("N","NE","E","SE","S","SO","O","NO")
  ) +
  scale_colour_manual(values = paleta_clases, drop = FALSE, name = "Class") +
  scale_y_continuous(name = expression("Corrected wind speed (m s"^{-1}*")")) +
  coord_polar(theta = "x", start = 0, direction = 1) +
  labs(
    title    = "Drone movement direction vs. corrected wind speed by class",
    subtitle = "Angular position = drone going-to direction  |  Radius = wind speed"
  ) +
  theme_pub(base_size = 11) +
  theme(
    axis.title.x      = element_blank(),
    axis.text.x       = element_text(size = rel(0.95), face = "bold"),
    panel.grid.major  = element_line(colour = "grey80", linewidth = 0.3),
    panel.grid.minor  = element_line(colour = "grey92", linewidth = 0.2),
    legend.position   = "right"
  )

# ── 8g-ii. Polar facetado por clase ───────────────────────────────────────────
# Muestra la distribución de velocidades de viento para cada clase
# en función de la dirección de movimiento del dron

# Calcular media de velocidad por clase y bin angular de 20°
df_polar_mean <- df_polar %>%
  mutate(
    angle_bin = floor(angle_drone / 20) * 20 + 10   # centro del bin
  ) %>%
  group_by(Class, angle_bin) %>%
  summarise(
    mean_wind  = mean(speed_wind_corrected, na.rm = TRUE),
    sd_wind    = sd(speed_wind_corrected,   na.rm = TRUE),
    n          = n(),
    .groups    = "drop"
  ) %>%
  mutate(
    se_wind = sd_wind / sqrt(n),
    ymin    = pmax(mean_wind - se_wind, 0),
    ymax    = mean_wind + se_wind
  )

p_polar_facet <- ggplot(df_polar_mean,
                        aes(x = angle_bin, y = mean_wind, fill = Class)) +
  geom_col(width = 18, alpha = 0.80, colour = "grey20", linewidth = 0.2) +
  geom_errorbar(aes(ymin = ymin, ymax = ymax),
                width = 8, linewidth = 0.4, colour = "grey30") +
  scale_x_continuous(
    limits = c(0, 360),
    breaks = seq(0, 315, 45),
    labels = c("N","NE","E","SE","S","SO","O","NO")
  ) +
  scale_fill_manual(values = paleta_clases, drop = FALSE) +
  scale_y_continuous(name = expression("Mean wind speed (m s"^{-1}*")")) +
  coord_polar(theta = "x", start = 0, direction = 1) +
  facet_wrap(~ Class, ncol = 3) +
  labs(
    title    = "Mean wind speed by drone direction and morphological class",
    subtitle = "Bars = mean ± SE  |  Bin width = 20°"
  ) +
  theme_pub(base_size = 10) +
  theme(
    axis.title.x      = element_blank(),
    axis.text.x       = element_text(size = rel(0.85), face = "bold"),
    panel.grid.major  = element_line(colour = "grey80", linewidth = 0.3),
    panel.grid.minor  = element_line(colour = "grey92", linewidth = 0.2),
    legend.position   = "none",
    strip.text        = element_text(face = "bold", size = rel(1.0))
  )

# ── 8g-iii. Polar facetado por vídeo, coloreado por clase ─────────────────────
df_polar_video_mean <- df_polar %>%
  mutate(
    angle_bin = floor(angle_drone / 20) * 20 + 10
  ) %>%
  group_by(video_label, Class, angle_bin) %>%
  summarise(
    mean_wind = mean(speed_wind_corrected, na.rm = TRUE),
    n         = n(),
    .groups   = "drop"
  )

p_polar_video <- ggplot(df_polar_video_mean,
                        aes(x = angle_bin, y = mean_wind, fill = Class)) +
  geom_col(width = 18, alpha = 0.80, colour = "grey20", linewidth = 0.15) +
  scale_x_continuous(
    limits = c(0, 360),
    breaks = seq(0, 315, 45),
    labels = c("N","NE","E","SE","S","SO","O","NO")
  ) +
  scale_fill_manual(values = paleta_clases, drop = FALSE, name = "Class") +
  scale_y_continuous(name = expression("Mean wind speed (m s"^{-1}*")")) +
  coord_polar(theta = "x", start = 0, direction = 1) +
  facet_wrap(~ video_label, ncol = 2) +
  labs(
    title    = "Wind speed by drone direction, class and video",
    subtitle = "Bin width = 20°  |  Colour = dominant class"
  ) +
  theme_pub(base_size = 10) +
  theme(
    axis.title.x     = element_blank(),
    axis.text.x      = element_text(size = rel(0.80), face = "bold"),
    panel.grid.major = element_line(colour = "grey80", linewidth = 0.3),
    panel.grid.minor = element_line(colour = "grey92", linewidth = 0.2),
    legend.position  = "right",
    strip.text       = element_text(face = "bold")
  )

# ── 8g-iv. Polar facetado por sesión, coloreado por clase ────────────────────
df_polar_video_mean <- df_polar %>%
  mutate(angle_bin = floor(angle_drone / 20) * 20 + 10) %>%
  group_by(ID_label, Class, angle_bin) %>%
  summarise(
    mean_wind = mean(speed_wind_corrected, na.rm = TRUE),
    n         = n(),
    .groups   = "drop"
  )

p_polar_video <- ggplot(df_polar_video_mean,
                        aes(x = angle_bin, y = mean_wind, fill = Class)) +
  geom_col(width = 18, alpha = 0.80, colour = "grey20", linewidth = 0.15) +
  scale_x_continuous(
    limits = c(0, 360),
    breaks = seq(0, 315, 45),
    labels = c("N","NE","E","SE","S","SO","O","NO")
  ) +
  scale_fill_manual(values = paleta_clases, drop = FALSE, name = "Class") +
  scale_y_continuous(name = expression("Mean wind speed (m s"^{-1}*")")) +
  coord_polar(theta = "x", start = 0, direction = 1) +
  facet_wrap(~ ID_label, ncol = 2) +
  labs(
    title    = "Wind speed by drone direction, class and ID",
    subtitle = "Bin width = 20°  |  Colour = dominant class"
  ) +
  theme_pub(base_size = 10) +
  theme(
    axis.title.x     = element_blank(),
    axis.text.x      = element_text(size = rel(0.80), face = "bold"),
    panel.grid.major = element_line(colour = "grey80", linewidth = 0.3),
    panel.grid.minor = element_line(colour = "grey92", linewidth = 0.2),
    legend.position  = "right",
    strip.text       = element_text(face = "bold")
  )

# ── 8g-v. Rose diagram: frecuencia de dirección del dron por clase ───────────
# Complementa los anteriores mostrando cuántas observaciones hay
# en cada dirección, independientemente de la velocidad del viento

df_rose <- df_polar %>%
  mutate(
    angle_bin = floor(angle_drone / 20) * 20 + 10
  ) %>%
  group_by(Class, angle_bin) %>%
  summarise(n = n(), .groups = "drop") %>%
  group_by(Class) %>%
  mutate(prop = n / sum(n) * 100) %>%
  ungroup()

p_rose <- ggplot(df_rose,
                 aes(x = angle_bin, y = prop, fill = Class)) +
  geom_col(width = 18, alpha = 0.80, colour = "grey20", linewidth = 0.2) +
  scale_x_continuous(
    limits = c(0, 360),
    breaks = seq(0, 315, 45),
    labels = c("N","NE","E","SE","S","SO","O","NO")
  ) +
  scale_fill_manual(values = paleta_clases, drop = FALSE) +
  scale_y_continuous(name = "Frequency (%)") +
  coord_polar(theta = "x", start = 0, direction = 1) +
  facet_wrap(~ Class, ncol = 3) +
  labs(
    title    = "Rose diagram: drone movement direction by morphological class",
    subtitle = "Radius = % of observations in each 20° directional bin"
  ) +
  theme_pub(base_size = 10) +
  theme(
    axis.title.x     = element_blank(),
    axis.text.x      = element_text(size = rel(0.85), face = "bold"),
    panel.grid.major = element_line(colour = "grey80", linewidth = 0.3),
    panel.grid.minor = element_line(colour = "grey92", linewidth = 0.2),
    legend.position  = "none",
    strip.text       = element_text(face = "bold", size = rel(1.0))
  )

# ── 8h. CORRELACIÓN CIRCULAR: CORRIENTE ~ DRON ───────────────────────────────

# Filtro de datos válidos para ángulos de corriente y dron
df <- df %>%
  mutate(
    angle_current = (atan2(u_current, v_current) * 180 / pi) %% 360,
    delta_angle_cd = ((angle_current - angle_drone) + 180) %% 360 - 180
  )

df_ang_cd <- df %>%
  filter(!is.na(video_label),
         !is.na(angle_current), !is.na(angle_drone),
         !is.na(speed_current), !is.na(speed_drone),
         speed_current > 0, speed_drone > 0)

cat("\n", strrep("=", 70), "\n")
cat("  CORRELACIÓN CIRCULAR (Jammalamadaka-Sarma): Corriente ~ Dron\n")
cat(strrep("=", 70), "\n\n")
cat("Filas usadas (ángulos válidos):", nrow(df_ang_cd), "\n\n")

# ── Test global ───────────────────────────────────────────────────────────────
js_global_cd <- circ_cor_js(df_ang_cd$angle_current,
                            df_ang_cd$angle_drone)

cat(sprintf("Global  r_c = %.4f  T = %.4f  p %s\n",
            js_global_cd$r,
            js_global_cd$T_stat,
            ifelse(js_global_cd$p < 0.001, "< 0.001",
                   paste0("= ", round(js_global_cd$p, 4)))))

# ── Tests por vídeo ───────────────────────────────────────────────────────────
cat("\nPor vídeo:\n")
ang_cd_video_stats <- df_ang_cd %>%
  group_by(video_label) %>%
  summarise(
    n          = n(),
    .circ      = list(
      if (n() >= 5)
        circ_cor_js(angle_current, angle_drone)
      else
        list(r = NA_real_, T_stat = NA_real_, p = NA_real_)
    ),
    mean_delta = mean(delta_angle_cd, na.rm = TRUE),
    sd_delta   = sd(delta_angle_cd,   na.rm = TRUE),
    .groups    = "drop"
  ) %>%
  mutate(
    r_c    = sapply(.circ, `[[`, "r"),
    T_stat = sapply(.circ, `[[`, "T_stat"),
    p_val  = sapply(.circ, `[[`, "p")
  ) %>%
  select(-".circ")
print(ang_cd_video_stats)

# ── Tests por sesión ──────────────────────────────────────────────────────────
cat("\nPor sesión:\n")
ang_cd_ID_stats <- df_ang_cd %>%
  group_by(ID_label) %>%
  summarise(
    n          = n(),
    .circ      = list(
      if (n() >= 5)
        circ_cor_js(angle_current, angle_drone)
      else
        list(r = NA_real_, T_stat = NA_real_, p = NA_real_)
    ),
    mean_delta = mean(delta_angle_cd, na.rm = TRUE),
    sd_delta   = sd(delta_angle_cd,   na.rm = TRUE),
    .groups    = "drop"
  ) %>%
  mutate(
    r_c    = sapply(.circ, `[[`, "r"),
    T_stat = sapply(.circ, `[[`, "T_stat"),
    p_val  = sapply(.circ, `[[`, "p")
  ) %>%
  select(-".circ")
print(ang_cd_ID_stats)

# ── Etiquetas para gráficas ───────────────────────────────────────────────────
lbl_global_cd <- if (!is.na(js_global_cd$r)) {
  sprintf("r\u1d9c = %.2f\np %s",
          js_global_cd$r,
          ifelse(js_global_cd$p < 0.001, "< 0.001",
                 paste0("= ", round(js_global_cd$p, 3))))
} else { "n.d." }

ann_global_cd <- data.frame(x = Inf, y = -Inf, label = lbl_global_cd)

lab_ang_cd_vid <- ang_cd_video_stats %>%
  mutate(lbl = ifelse(!is.na(r_c),
                      sprintf("r\u1d9c = %.2f\np %s", r_c,
                              ifelse(p_val < 0.001, "< 0.001",
                                     paste0("= ", round(p_val, 3)))),
                      "n.d."))

lab_ang_cd_ID <- ang_cd_ID_stats %>%
  mutate(lbl = ifelse(!is.na(r_c),
                      sprintf("r\u1d9c = %.2f\np %s", r_c,
                              ifelse(p_val < 0.001, "< 0.001",
                                     paste0("= ", round(p_val, 3)))),
                      "n.d."))

# ── Scatter global ────────────────────────────────────────────────────────────
p_ang_cd_global <- ggplot(df_ang_cd,
                          aes(x = angle_current, y = angle_drone,
                              colour = ID_label)) +
  geom_abline(slope = 1, intercept = 0,
              linetype = "dashed", colour = "grey60", linewidth = 0.5) +
  geom_point(alpha = 0.35, size = 0.8, shape = 16) +
  geom_smooth(aes(group = 1), method = "lm", se = TRUE,
              colour = "black", fill = "grey80", linewidth = 0.7) +
  geom_text(data = ann_global_cd,
            aes(x = x, y = y, label = label),
            inherit.aes = FALSE,
            hjust = 1.05, vjust = -0.4,
            size = 3.5, fontface = "bold", lineheight = 1.2) +
  scale_colour_manual(values = paleta_IDs, name = "ID") +
  scale_x_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°"),
                     limits = c(0, 360)) +
  scale_y_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°"),
                     limits = c(0, 360)) +
  coord_fixed() +
  labs(title    = "Current direction vs. drone direction",
       subtitle = "Jammalamadaka\u2013Sarma circular correlation",
       x = "Current direction (°, going-to)",
       y = "Drone direction (°, going-to)") +
  theme_pub(base_size = 12) +
  guides(colour = guide_legend(override.aes = list(size = 2.5, alpha = 1)))

# ── Scatter facetado por sesión ───────────────────────────────────────────────
p_ang_cd_session <- ggplot(df_ang_cd,
                           aes(x = angle_current, y = angle_drone,
                               colour = ID_label)) +
  geom_abline(slope = 1, intercept = 0,
              linetype = "dashed", colour = "grey65", linewidth = 0.45) +
  geom_point(alpha = 0.40, size = 0.75, shape = 16) +
  geom_smooth(method = "lm", se = TRUE,
              linewidth = 0.65, fill = "grey85") +
  geom_text(data = lab_ang_cd_ID,
            aes(x = Inf, y = -Inf, label = lbl),
            inherit.aes = FALSE, hjust = 1.05, vjust = -0.4,
            size = 2.8, fontface = "italic", lineheight = 1.1) +
  scale_colour_manual(values = paleta_IDs) +
  scale_x_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°")) +
  scale_y_continuous(breaks = seq(0, 360, 90),
                     labels = c("0°","90°","180°","270°","360°")) +
  facet_wrap(~ ID_label, scales = "free") +
  labs(title    = "Current direction vs. drone direction — by ID",
       subtitle = "Jammalamadaka\u2013Sarma circular correlation",
       x = "Current direction (°, going-to)",
       y = "Drone direction (°, going-to)") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")

# ── Histograma diferencia angular (corriente - dron) por sesión ───────────────
p_delta_cd <- ggplot(df_ang_cd,
                     aes(x = delta_angle_cd, fill = ID_label)) +
  geom_histogram(binwidth = 15, colour = "grey20", linewidth = 0.25,
                 alpha = 0.80, position = "identity") +
  geom_vline(xintercept = 0, colour = "black",
             linetype = "dashed", linewidth = 0.6) +
  scale_fill_manual(values = paleta_IDs) +
  scale_x_continuous(breaks = seq(-180, 180, 60),
                     labels = c("-180°","-120°","-60°","0°","60°","120°","180°")) +
  facet_wrap(~ ID_label, scales = "free_y", ncol = 2) +
  labs(title    = "Angular difference: current direction \u2212 drone direction",
       subtitle = "Dashed line at 0\u00b0 = same direction  |  \u00b1180\u00b0 = opposing",
       x = "Angular difference (°)", y = "Count") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")

# ── Diferencia angular absoluta ───────────────────────────────────────────────
df_ang_cd <- df_ang_cd %>%
  mutate(abs_delta_cd = abs(delta_angle_cd))

# Resumen por sesión
cat("\n", strrep("=", 70), "\n")
cat("  DIFERENCIA ANGULAR ABSOLUTA |corriente - drone| POR SESIÓN\n")
cat(strrep("=", 70), "\n\n")

abs_cd_stats <- df_ang_cd %>%
  group_by(ID_label) %>%
  summarise(
    n            = n(),
    mean_abs     = mean(abs_delta_cd,   na.rm = TRUE),
    sd_abs       = sd(abs_delta_cd,     na.rm = TRUE),
    median_abs   = median(abs_delta_cd, na.rm = TRUE),
    q25          = quantile(abs_delta_cd, 0.25, na.rm = TRUE),
    q75          = quantile(abs_delta_cd, 0.75, na.rm = TRUE),
    pct_below_45 = mean(abs_delta_cd <  45, na.rm = TRUE) * 100,
    pct_below_90 = mean(abs_delta_cd <  90, na.rm = TRUE) * 100,
    .groups = "drop"
  )
print(abs_cd_stats)

# Kruskal-Wallis entre sesiones
kw_cd <- kruskal.test(abs_delta_cd ~ ID_label, data = df_ang_cd)
cat(sprintf("\nKruskal-Wallis entre sesiones: chi² = %.4f  df = %d  p %s\n",
            kw_cd$statistic, kw_cd$parameter,
            ifelse(kw_cd$p.value < 0.001, "< 0.001",
                   paste0("= ", round(kw_cd$p.value, 4)))))

# Dunn post-hoc
cat("\nDunn post-hoc (BH correction):\n")
cat(strrep("-", 50), "\n")
dunn_cd <- dunn.test::dunn.test(df_ang_cd$abs_delta_cd,
                                df_ang_cd$ID_label,
                                method = "bh", altp = TRUE)

# ── Boxplot |Δθ| corriente-dron por sesión ────────────────────────────────────
kw_cd_lbl <- sprintf("Kruskal\u2013Wallis: \u03c7\u00b2 = %.2f, df = %d, p %s",
                     kw_cd$statistic, kw_cd$parameter,
                     ifelse(kw_cd$p.value < 0.001, "< 0.001",
                            paste0("= ", round(kw_cd$p.value, 3))))

p_abs_cd_box <- ggplot(df_ang_cd,
                       aes(x = ID_label, y = abs_delta_cd, fill = ID_label)) +
  geom_boxplot(outlier.shape = 1, outlier.size = 0.9,
               outlier.colour = "grey50",
               alpha = 0.75, linewidth = 0.35) +
  geom_hline(yintercept = c(45, 90),
             linetype = "dashed", colour = "grey40", linewidth = 0.4) +
  annotate("text", x = 0.55, y = 46, label = "45°",
           size = 3, colour = "grey40", vjust = -0.3) +
  annotate("text", x = 0.55, y = 91, label = "90°",
           size = 3, colour = "grey40", vjust = -0.3) +
  scale_fill_manual(values = paleta_IDs) +
  scale_y_continuous(breaks = seq(0, 180, 30),
                     labels = paste0(seq(0, 180, 30), "°"),
                     limits = c(0, 185)) +
  labs(title    = "Absolute angular difference |current \u2212 drone| by ID",
       subtitle = kw_cd_lbl,
       x = NULL, y = "|\u0394\u03b8| (°)") +
  theme_pub(base_size = 12) +
  theme(legend.position = "none",
        axis.text.x     = element_text(angle = 30, hjust = 1))

# ── Histograma |Δθ| por sesión ────────────────────────────────────────────────
p_abs_cd_hist <- ggplot(df_ang_cd,
                        aes(x = abs_delta_cd, fill = ID_label)) +
  geom_histogram(binwidth = 10, colour = "grey20",
                 linewidth = 0.25, alpha = 0.80) +
  geom_vline(xintercept = c(45, 90),
             linetype = "dashed", colour = "grey30", linewidth = 0.5) +
  scale_fill_manual(values = paleta_IDs) +
  scale_x_continuous(breaks = seq(0, 180, 30),
                     labels = paste0(seq(0, 180, 30), "°"),
                     limits = c(0, 180)) +
  facet_wrap(~ ID_label, scales = "free_y", ncol = 2) +
  labs(title    = "Distribution of |current \u2212 drone| angular difference",
       subtitle = "Dashed lines at 45° and 90°",
       x = "|\u0394\u03b8| (°)", y = "Count") +
  theme_pub(base_size = 10) +
  theme(legend.position = "none")

# ── ECDF |Δθ| por sesión ─────────────────────────────────────────────────────
p_abs_cd_ecdf <- ggplot(df_ang_cd,
                        aes(x = abs_delta_cd, colour = ID_label)) +
  stat_ecdf(linewidth = 0.7) +
  geom_vline(xintercept = c(45, 90),
             linetype = "dashed", colour = "grey40", linewidth = 0.4) +
  scale_colour_manual(values = paleta_IDs, name = "ID") +
  scale_x_continuous(breaks = seq(0, 180, 30),
                     labels = paste0(seq(0, 180, 30), "°"),
                     limits = c(0, 180)) +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(title    = "Cumulative distribution of |\u0394\u03b8| (current \u2212 drone)",
       subtitle = "Proportion of observations below each angular threshold",
       x = "|\u0394\u03b8| (°)", y = "Cumulative frequency") +
  theme_pub(base_size = 12) +
  guides(colour = guide_legend(override.aes = list(linewidth = 1.5)))

# ── 9. EXPORTAR GRÁFICAS ──────────────────────────────────────────────────────
output_dir <- dirname(file_path)

ggsave(file.path(output_dir, "01_class_total.png"),
       p_total,      width = 8,  height = 5, dpi = 180)
ggsave(file.path(output_dir, "02_class_by_video.png"),
       p_video,      width = 14, height = 8, dpi = 180)
ggsave(file.path(output_dir, "03_heatmap_classes.png"),
       p_heat,       width = 10, height = 5, dpi = 180)
ggsave(file.path(output_dir, "04_boxplots_speed.png"),
       p_box,        width = 12, height = 8, dpi = 180)
ggsave(file.path(output_dir, "05_corr_wind_dron_global.png"),
       p_wd_global,  width = 9,  height = 6, dpi = 180)
ggsave(file.path(output_dir, "06_corr_wind_dron_video.png"),
       p_wd_video,   width = 12, height = 8, dpi = 180)
ggsave(file.path(output_dir, "07_corr_current_dron_global.png"),
       p_cd_global,  width = 9,  height = 6, dpi = 180)
ggsave(file.path(output_dir, "08_corr_current_dron_video.png"),
       p_cd_video,   width = 12, height = 8, dpi = 180)
ggsave(file.path(output_dir, "09_class_vs_wind.png"),
       p_class_wind, width = 12, height = 9, dpi = 180)
ggsave(file.path(output_dir, "10_class_vs_current.png"),
       p_class_curr, width = 12, height = 9, dpi = 180)
ggsave(file.path(output_dir, "11_angle_corr_wind_drone_global.png"),
       p_ang_global, width = 7,  height = 7, dpi = 180)
ggsave(file.path(output_dir, "12_angle_corr_wind_drone_video.png"),
       p_ang_video,  width = 12, height = 9, dpi = 180)
ggsave(file.path(output_dir, "13_delta_angle_histogram.png"),
       p_delta,      width = 12, height = 8, dpi = 180)
ggsave(file.path(output_dir, "14_abs_delta_boxplot.png"),
       p_abs_box,  width = 10, height = 6, dpi = 180)
ggsave(file.path(output_dir, "15_abs_delta_histogram.png"),
       p_abs_hist, width = 12, height = 8, dpi = 180)
ggsave(file.path(output_dir, "16_abs_delta_ecdf.png"),
       p_abs_ecdf, width = 9,  height = 6, dpi = 180)
ggsave(file.path(output_dir, "17_polar_class_wind.png"),
       p_polar_class, width = 9,  height = 7,  dpi = 180)
ggsave(file.path(output_dir, "18_polar_facet_class.png"),
       p_polar_facet, width = 12, height = 8,  dpi = 180)
ggsave(file.path(output_dir, "19_polar_facet_video.png"),
       p_polar_video, width = 12, height = 10, dpi = 180)
ggsave(file.path(output_dir, "20_rose_diagram.png"),
       p_rose,        width = 12, height = 8,  dpi = 180)
ggsave(file.path(output_dir, "21_angle_corr_current_drone_global.png"),
       p_ang_cd_global,  width = 7,  height = 7,  dpi = 180)
ggsave(file.path(output_dir, "22_angle_corr_current_drone_session.png"),
       p_ang_cd_session, width = 12, height = 9,  dpi = 180)
ggsave(file.path(output_dir, "23_delta_angle_cd_histogram.png"),
       p_delta_cd,       width = 12, height = 8,  dpi = 180)
ggsave(file.path(output_dir, "24_abs_delta_cd_boxplot.png"),
       p_abs_cd_box,     width = 10, height = 6,  dpi = 180)
ggsave(file.path(output_dir, "25_abs_delta_cd_histogram.png"),
       p_abs_cd_hist,    width = 12, height = 8,  dpi = 180)
ggsave(file.path(output_dir, "26_abs_delta_cd_ecdf.png"),
       p_abs_cd_ecdf,    width = 9,  height = 6,  dpi = 180)

cat("Gráficas guardadas en:", output_dir, "\n")

# ── 10. EXPORTAR RESULTADOS A CSV ─────────────────────────────────────────────
write.csv(normality_df,
          file.path(output_dir, "resultados_normalidad.csv"),
          row.names = FALSE)
write.csv(homoscedasticity_results,
          file.path(output_dir, "resultados_homocedasticidad.csv"),
          row.names = FALSE)

cat("Tablas de resultados exportadas.\n")

# ── 11. MOSTRAR GRÁFICAS EN PANTALLA ──────────────────────────────────────────
print(p_total)
print(p_video)
print(p_heat)
print(p_box)
print(p_wd_global)
print(p_wd_video)
print(p_cd_global)
print(p_cd_video)
print(p_class_wind)
print(p_class_curr)

cat("\n¡Análisis completado!\n")

