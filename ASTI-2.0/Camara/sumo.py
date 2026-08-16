import cv2
import numpy as np
from picamera2 import Picamera2

# Inicializar la cámara
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# Valores del color del enemigo (ajustados para el rival blanco)
lower_bound = np.array([0, 0, 78])
upper_bound = np.array([179, 50, 255])

# Crear el "pincel" matemático para los filtros morfológicos
kernel = np.ones((5, 5), np.uint8)

print("Iniciando Radar de Sumo con Filtros Morfológicos...")
print("Presiona 'q' en la ventana de vídeo para salir.")

try:
    while True:
        # Capturar fotograma
        frame = picam2.capture_array()
        
        # ==========================================
        # 1. EL FILTRO DE COLOR Y LIMPIEZA
        # ==========================================
        # A. Desenfoque ligero para eliminar el granulado de la cámara
        frame_suavizado = cv2.GaussianBlur(frame, (5, 5), 0)
        
        # B. Conversión y Máscara Binaria
        hsv = cv2.cvtColor(frame_suavizado, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # C. Limpieza Morfológica (Erosión + Dilatación)
        # Borra la basura pequeña y luego rellena los agujeros del objetivo
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        # Imagen a color para dibujar la telemetría encima
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # ==========================================
        # 2. EL FILTRO DE FORMA (El francotirador)
        # ==========================================
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        enemigo_detectado = False
        
        for contorno in contornos:
            area = cv2.contourArea(contorno)
            
            # FILTRO A: Área mínima (Ajustar en pista según la distancia)
            if area > 1500:
                x, y, w, h = cv2.boundingRect(contorno)
                
                # FILTRO B: Proporciones (Aspect Ratio para detectar cajas)
                aspect_ratio = float(w) / h
                
                if 0.6 < aspect_ratio < 1.5:
                    enemigo_detectado = True
                    
                    # Calcular el centro para embestir
                    cx = x + (w // 2)
                    cy = y + (h // 2)
                    error_ataque = cx - 320 # Asumiendo 640px de ancho
                    
                    # Dibujar interfaz de ataque (Caja verde y punto rojo)
                    cv2.rectangle(frame_bgr, (x, y), (x+w, y+h), (0, 255, 0), 3)
                    cv2.circle(frame_bgr, (cx, cy), 6, (0, 0, 255), -1)
                    cv2.putText(frame_bgr, f"RIVAL FIJADO (Err: {error_ataque})", (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    print(f"¡Atacando! Error de dirección: {error_ataque}px")
                    
                    # Rompemos el bucle para centrarnos solo en esta amenaza
                    break

        if not enemigo_detectado:
            print("Buscando objetivo...")
            cv2.putText(frame_bgr, "ESCANEO ACTIVO", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            
        # Mostrar las pantallas
        cv2.imshow('Camara Sumo', frame_bgr)
        cv2.imshow('Mascara Sumo (Limpia)', mask)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    picam2.stop()
    cv2.destroyAllWindows()