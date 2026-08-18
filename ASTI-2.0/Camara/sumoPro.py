import cv2
import numpy as np
from picamera2 import Picamera2

# ==========================================
# CONFIGURACIÓN MODO TORNEO
# ==========================================
MODO_DEBUG = True  

picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (320, 240)},
    sensor={"framerate": 60}
)
picam2.configure(config)
picam2.start()

lower_negro = np.array([0, 0, 0])
upper_negro = np.array([179, 255, 60]) 
lower_blanco = np.array([0, 0, 150]) 
upper_blanco = np.array([179, 50, 255])

# Kernel más pequeño por la reducción de resolución
kernel = np.ones((3, 3), np.uint8) 

print("Iniciando Sumo ULTRARRÁPIDO...")

try:
    while True:
        frame = picam2.capture_array()
        
        # Desenfoque menor (3x3 en vez de 5x5)
        frame_suavizado = cv2.GaussianBlur(frame, (3, 3), 0)
        hsv = cv2.cvtColor(frame_suavizado, cv2.COLOR_RGB2HSV)
        
        if MODO_DEBUG:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # ==============================================================
        # PRIORIDAD 1: SUPERVIVENCIA (Franja inferior escalada)
        # ==============================================================
        roi_suelo = hsv[200:240, 0:320]
        mask_negro = cv2.inRange(roi_suelo, lower_negro, upper_negro)
        
        area_negra_frente = cv2.countNonZero(mask_negro)
        
        if MODO_DEBUG:
            cv2.rectangle(frame_bgr, (0, 200), (320, 240), (0, 255, 255), 1)

        # Área escalada al nuevo tamaño (antes 1000, ahora 250)
        if area_negra_frente > 250:
            print("¡PELIGRO! Borde negro. ¡FRENANDO!")
            
            if MODO_DEBUG:
                cv2.putText(frame_bgr, "ALARMA NEGRO!", (70, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('Camara Sumo', frame_bgr)
                cv2.imshow('Mascara Negro', mask_negro)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            continue 

        # ==============================================================
        # PRIORIDAD 2: ATAQUE
        # ==============================================================
        mask_enemigo = cv2.inRange(hsv, lower_blanco, upper_blanco)
        mask_enemigo = cv2.erode(mask_enemigo, kernel, iterations=1)
        mask_enemigo = cv2.dilate(mask_enemigo, kernel, iterations=2)
        
        contornos, _ = cv2.findContours(mask_enemigo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        enemigo_detectado = False
        
        for contorno in contornos:
            area = cv2.contourArea(contorno)
            
            # Área de detección enemiga escalada (antes 1500, ahora 400)
            if area > 400:
                x, y, w, h = cv2.boundingRect(contorno)
                aspect_ratio = float(w) / h
                
                if 0.6 < aspect_ratio < 1.5:
                    enemigo_detectado = True
                    cx = x + (w // 2)
                    cy = y + (h // 2)
                    error_ataque = cx - 160
                    
                    print(f"¡Atacando! Error: {error_ataque}px")
                    
                    if MODO_DEBUG:
                        cv2.rectangle(frame_bgr, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.circle(frame_bgr, (cx, cy), 4, (0, 0, 255), -1)
                        cv2.putText(frame_bgr, f"RIVAL (Err: {error_ataque})", (x, y - 5), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                    break

        if not enemigo_detectado and MODO_DEBUG:
            cv2.putText(frame_bgr, "BUSCANDO...", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
            
        if MODO_DEBUG:
            cv2.imshow('Camara Sumo', frame_bgr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
finally:
    picam2.stop()
    if MODO_DEBUG:
        cv2.destroyAllWindows()