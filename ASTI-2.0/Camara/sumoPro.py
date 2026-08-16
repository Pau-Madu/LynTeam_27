import cv2
import numpy as np
from picamera2 import Picamera2

# Inicializar la cámara
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# --- CALIBRACIÓN DE COLORES ---
# 1. El color de la LÍNEA (Negro) -> El brillo (Value) es muy bajo
lower_negro = np.array([0, 0, 0])
upper_negro = np.array([179, 255, 60]) # V hasta 60 para atrapar grises muy oscuros

# 2. El color del ENEMIGO (Blanco)
lower_blanco = np.array([0, 0, 150]) # V alto para que sea blanco brillante
upper_blanco = np.array([179, 50, 255])

kernel = np.ones((5, 5), np.uint8)

print("Iniciando Sistema de Combate: Supervivencia + Ataque")
print("Presiona 'q' para salir.")

try:
    while True:
        frame = picam2.capture_array()
        frame_suavizado = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(frame_suavizado, cv2.COLOR_RGB2HSV)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # ==============================================================
        # PRIORIDAD 1: SUPERVIVENCIA (DETECTAR LÍNEA NEGRA EN EL MORRO)
        # ==============================================================
        # Recortamos SOLO la parte más baja de la imagen (los últimos 80 píxeles)
        roi_suelo = hsv[400:480, 0:640]
        mask_negro = cv2.inRange(roi_suelo, lower_negro, upper_negro)
        
        # Contamos cuántos píxeles negros hay justo delante de nosotros
        area_negra_frente = cv2.countNonZero(mask_negro)
        
        # Dibujamos una caja de advertencia en la pantalla para depurar
        cv2.rectangle(frame_bgr, (0, 400), (640, 480), (0, 255, 255), 2)

        # Si el área negra supera un límite, ¡estamos pisando el borde!
        if area_negra_frente > 1000: # Ajustar este número en el ring
            print("¡PELIGRO! Borde negro detectado. ¡FRENANDO!")
            cv2.putText(frame_bgr, "¡ALARMA LÍNEA NEGRA!", (150, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            # --- AQUÍ IRÍA LA ORDEN A LOS MOTORES ---
            # motores.retroceder()
            # motores.girar_180()
            
            # MUY IMPORTANTE: Usamos 'continue' para saltarnos el ataque este turno
            # Si estamos a punto de caer, ignoramos al enemigo.
            cv2.imshow('Camara Sumo', frame_bgr)
            cv2.imshow('Mascara Negro (Suelo)', mask_negro)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue 

        # ==============================================================
        # PRIORIDAD 2: ATAQUE (DETECTAR AL RIVAL)
        # ==============================================================
        # Si hemos llegado hasta esta línea de código, significa que estamos a salvo en el centro del ring
        
        mask_enemigo = cv2.inRange(hsv, lower_blanco, upper_blanco)
        mask_enemigo = cv2.erode(mask_enemigo, kernel, iterations=1)
        mask_enemigo = cv2.dilate(mask_enemigo, kernel, iterations=2)
        
        contornos, _ = cv2.findContours(mask_enemigo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        enemigo_detectado = False
        
        for contorno in contornos:
            area = cv2.contourArea(contorno)
            if area > 1500:
                x, y, w, h = cv2.boundingRect(contorno)
                aspect_ratio = float(w) / h
                
                if 0.6 < aspect_ratio < 1.5:
                    enemigo_detectado = True
                    cx = x + (w // 2)
                    cy = y + (h // 2)
                    error_ataque = cx - 320
                    
                    cv2.rectangle(frame_bgr, (x, y), (x+w, y+h), (0, 255, 0), 3)
                    cv2.circle(frame_bgr, (cx, cy), 6, (0, 0, 255), -1)
                    cv2.putText(frame_bgr, f"RIVAL FIJADO (Err: {error_ataque})", (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    print(f"¡Atacando! Error: {error_ataque}px")
                    break

        if not enemigo_detectado:
            cv2.putText(frame_bgr, "BUSCANDO...", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            
        cv2.imshow('Camara Sumo', frame_bgr)
        # Opcional: Mostrar la máscara del enemigo en lugar de la del suelo
        # cv2.imshow('Mascara Enemigo', mask_enemigo) 
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    picam2.stop()
    cv2.destroyAllWindows()