import cv2
import numpy as np
from picamera2 import Picamera2

# ==========================================
# CONFIGURACIÓN MODO TORNEO
# ==========================================
MODO_DEBUG = True  # Cambiar a False el día de la carrera

picam2 = Picamera2()
# Resolución 320x240 a 60 FPS (Procesa 4 veces más rápido)
config = picam2.create_preview_configuration(
    main={"size": (320, 240)},
    sensor={"framerate": 60} 
)
picam2.configure(config)
picam2.start()

lower_bound = np.array([0, 0, 78])
upper_bound = np.array([179, 50, 255])

print("Iniciando seguimiento de línea ULTRARRÁPIDO...")
if not MODO_DEBUG:
    print("MODO COMPETICIÓN: Pantallas apagadas, máxima velocidad.")

try:
    while True:
        frame = picam2.capture_array()
        
        # ROI Escalada: Mitad inferior (de la fila 120 a la 240)
        roi = frame[120:240, 0:320]

        hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # Solo dibujamos la interfaz si estamos debuggeando
        if MODO_DEBUG:
            roi_bgr = cv2.cvtColor(roi, cv2.COLOR_RGB2BGR)

        momentos = cv2.moments(mask)
        
        # Parámetros escalados a la nueva resolución (320x240)
        centro_imagen = 160
        margen = 20 # Tolerancia más pequeña

        if momentos["m00"] > 0:
            cx = int(momentos["m10"] / momentos["m00"])
            cy = int(momentos["m01"] / momentos["m00"])

            # CÁLCULO DEL ERROR PURO
            error = cx - centro_imagen

            # Opcional: print(f"Error de dirección: {error}")

            if MODO_DEBUG:
                cv2.circle(roi_bgr, (cx, cy), 5, (0, 0, 255), -1)
                cv2.line(roi_bgr, (centro_imagen, cy), (cx, cy), (0, 255, 255), 2)

                if error < -margen:
                    color_texto = (0, 165, 255)
                    cv2.putText(roi_bgr, f"<- IZQ (Err: {error})", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_texto, 1)
                elif error > margen:
                    color_texto = (0, 165, 255)
                    cv2.putText(roi_bgr, f"DER -> (Err: {error})", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_texto, 1)
                else:
                    color_texto = (0, 255, 0)
                    cv2.putText(roi_bgr, f"^^ RECTO (Err: {error})", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_texto, 1)
                
        else:
            if MODO_DEBUG:
                cv2.putText(roi_bgr, "BUSCANDO PISTA", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Renderizado de pantallas (Solo si Debug está activo)
        if MODO_DEBUG:
            cv2.line(roi_bgr, (centro_imagen, 0), (centro_imagen, 120), (255, 0, 0), 1)
            cv2.line(roi_bgr, (centro_imagen - margen, 0), (centro_imagen - margen, 120), (0, 255, 0), 1)
            cv2.line(roi_bgr, (centro_imagen + margen, 0), (centro_imagen + margen, 120), (0, 255, 0), 1)
            
            cv2.imshow('Camara F1 (ROI)', roi_bgr)
            cv2.imshow('Mascara (ROI)', mask)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
finally:
    picam2.stop()
    if MODO_DEBUG:
        cv2.destroyAllWindows()