import cv2
import numpy as np

# ==========================================
# CONFIGURACIÓN MODO TORNEO
# ==========================================
LOWER_BOUND = np.array([0, 0, 78])
UPPER_BOUND = np.array([179, 50, 255])
CENTRO_IMAGEN = 160
MARGEN = 20

def procesar_vision(frame_bgr, modo_debug=True):
    """
    Recibe un frame en formato BGR (320x240) desde el cerebro.
    Si modo_debug es True, dibuja la interfaz y abre ventanas para calibrar.
    Devuelve el error de giro para los motores.
    """
    # ROI Escalada: Mitad inferior (de la fila 120 a la 240)
    roi = frame_bgr[120:240, 0:320]

    # Conversión a HSV (el Cerebro ya nos manda BGR)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_BOUND, UPPER_BOUND)
    
    # Solo duplicamos el frame para dibujar si estamos debuggeando
    roi_dibujado = roi.copy() if modo_debug else None

    momentos = cv2.moments(mask)
    error = 0 # Valor por defecto si perdemos la línea

    if momentos["m00"] > 0:
        cx = int(momentos["m10"] / momentos["m00"])
        cy = int(momentos["m01"] / momentos["m00"])

        # CÁLCULO DEL ERROR PURO
        error = cx - CENTRO_IMAGEN

        # Dibujamos solo si Debug está activo
        if modo_debug:
            cv2.circle(roi_dibujado, (cx, cy), 5, (0, 0, 255), -1)
            cv2.line(roi_dibujado, (CENTRO_IMAGEN, cy), (cx, cy), (0, 255, 255), 2)

            if error < -MARGEN:
                color_texto = (0, 165, 255)
                cv2.putText(roi_dibujado, f"<- IZQ (Err: {error})", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_texto, 1)
            elif error > MARGEN:
                color_texto = (0, 165, 255)
                cv2.putText(roi_dibujado, f"DER -> (Err: {error})", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_texto, 1)
            else:
                color_texto = (0, 255, 0)
                cv2.putText(roi_dibujado, f"^^ RECTO (Err: {error})", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_texto, 1)
            
    else:
        if modo_debug:
            cv2.putText(roi_dibujado, "BUSCANDO PISTA", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Renderizado de pantallas locales (Solo si Debug está activo)
    if modo_debug:
        cv2.line(roi_dibujado, (CENTRO_IMAGEN, 0), (CENTRO_IMAGEN, 120), (255, 0, 0), 1)
        cv2.line(roi_dibujado, (CENTRO_IMAGEN - MARGEN, 0), (CENTRO_IMAGEN - MARGEN, 120), (0, 255, 0), 1)
        cv2.line(roi_dibujado, (CENTRO_IMAGEN + MARGEN, 0), (CENTRO_IMAGEN + MARGEN, 120), (0, 255, 0), 1)
        
        cv2.imshow('Camara F1 (ROI)', roi_dibujado)
        cv2.imshow('Mascara (ROI)', mask)
        cv2.waitKey(1)

    return error