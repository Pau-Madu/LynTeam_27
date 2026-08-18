import cv2
import numpy as np

# ==========================================
# CONFIGURACIÓN MODO TORNEO (CONSTANTES)
# ==========================================
LOWER_NEGRO = np.array([0, 0, 0])
UPPER_NEGRO = np.array([179, 255, 60]) 
LOWER_BLANCO = np.array([0, 0, 150]) 
UPPER_BLANCO = np.array([179, 50, 255])

# Kernel más pequeño por la reducción de resolución
KERNEL = np.ones((3, 3), np.uint8) 

def procesar_sumo(frame_bgr, modo_debug=True):
    """
    Recibe un frame BGR (320x240) desde el Cerebro.
    Abre las ventanas de debug si se solicita.
    Devuelve una tupla: (accion, valor_error)
    """
    # Desenfoque menor (3x3 en vez de 5x5)
    frame_suavizado = cv2.GaussianBlur(frame_bgr, (3, 3), 0)
    
    # Como el frame del Cerebro ya es BGR, usamos COLOR_BGR2HSV
    hsv = cv2.cvtColor(frame_suavizado, cv2.COLOR_BGR2HSV)
    
    # Hacemos una copia para dibujar sin ensuciar el frame original que se manda a Unity
    frame_dibujado = frame_bgr.copy() if modo_debug else None

    # ==============================================================
    # PRIORIDAD 1: SUPERVIVENCIA (Franja inferior escalada)
    # ==============================================================
    roi_suelo = hsv[200:240, 0:320]
    mask_negro = cv2.inRange(roi_suelo, LOWER_NEGRO, UPPER_NEGRO)
    
    area_negra_frente = cv2.countNonZero(mask_negro)
    
    if modo_debug:
        cv2.rectangle(frame_dibujado, (0, 200), (320, 240), (0, 255, 255), 1)

    # Área escalada al nuevo tamaño (antes 1000, ahora 250)
    if area_negra_frente > 250:
        if modo_debug:
            cv2.putText(frame_dibujado, "ALARMA NEGRO!", (70, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow('Camara Sumo', frame_dibujado)
            cv2.imshow('Mascara Negro', mask_negro)
            cv2.waitKey(1)
            
        # Devolvemos PELIGRO inmediatamente para que el Cerebro mande marcha atrás a los motores
        return "PELIGRO", 0 

    # ==============================================================
    # PRIORIDAD 2: ATAQUE
    # ==============================================================
    mask_enemigo = cv2.inRange(hsv, LOWER_BLANCO, UPPER_BLANCO)
    mask_enemigo = cv2.erode(mask_enemigo, KERNEL, iterations=1)
    mask_enemigo = cv2.dilate(mask_enemigo, KERNEL, iterations=2)
    
    contornos, _ = cv2.findContours(mask_enemigo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        
        # Área de detección enemiga escalada (antes 1500, ahora 400)
        if area > 400:
            x, y, w, h = cv2.boundingRect(contorno)
            aspect_ratio = float(w) / h
            
            if 0.6 < aspect_ratio < 1.5:
                cx = x + (w // 2)
                cy = y + (h // 2)
                error_ataque = cx - 160
                
                if modo_debug:
                    cv2.rectangle(frame_dibujado, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.circle(frame_dibujado, (cx, cy), 4, (0, 0, 255), -1)
                    cv2.putText(frame_dibujado, f"RIVAL (Err: {error_ataque})", (x, y - 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                    
                    cv2.imshow('Camara Sumo', frame_dibujado)
                    cv2.waitKey(1)
                    
                # Devolvemos ATAQUE y el error para que el Cerebro mueva los motores hacia él
                return "ATAQUE", error_ataque

    # ==============================================================
    # MODO BÚSQUEDA (Si no hay peligro ni enemigo)
    # ==============================================================
    if modo_debug:
        cv2.putText(frame_dibujado, "BUSCANDO...", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
        cv2.imshow('Camara Sumo', frame_dibujado)
        cv2.waitKey(1)
        
    # Si no ha visto nada, mandamos BUSCANDO para que el Cerebro haga girar el robot sobre sí mismo
    return "BUSCANDO", 0