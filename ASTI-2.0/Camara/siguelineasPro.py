import cv2
import numpy as np
from picamera2 import Picamera2

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

lower_bound = np.array([0, 0, 78])
upper_bound = np.array([179, 50, 255])

print("Iniciando seguimiento de línea avanzado...")
print("Presiona 'q' para salir.")

try:
    while True:
        frame = picam2.capture_array()
        
        # 1. DEFINIR LA REGIÓN DE INTERÉS (ROI)
        # Nos quedamos solo con la mitad inferior de la imagen (de la fila 240 a la 480)
        # Esto quita el "ruido" del horizonte y hace que procese el doble de rápido
        roi = frame[240:480, 0:640]

        # Trabajamos la visión SOLO sobre el ROI
        hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        roi_bgr = cv2.cvtColor(roi, cv2.COLOR_RGB2BGR)

        momentos = cv2.moments(mask)
        
        # Parámetros del chasis y la cámara
        centro_imagen = 320
        margen = 40 

        if momentos["m00"] > 0:
            cx = int(momentos["m10"] / momentos["m00"])
            cy = int(momentos["m01"] / momentos["m00"])

            # 2. CÁLCULO DEL ERROR PARA EL FUTURO PID
            # Si cx = 320, el error es 0. Si cx = 100, el error es -220 (hay que girar mucho a la izq)
            error = cx - centro_imagen

            # Dibujar el punto central detectado
            cv2.circle(roi_bgr, (cx, cy), 10, (0, 0, 255), -1)
            # Dibujar una línea de vector desde el centro de la cámara hasta la línea
            cv2.line(roi_bgr, (centro_imagen, cy), (cx, cy), (0, 255, 255), 2)

            if error < -margen:
                direccion = f"<- IZQ (Err: {error})"
                color_texto = (0, 165, 255)
            elif error > margen:
                direccion = f"DER -> (Err: {error})"
                color_texto = (0, 165, 255)
            else:
                direccion = f"^^ RECTO (Err: {error})"
                color_texto = (0, 255, 0)

            cv2.putText(roi_bgr, direccion, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_texto, 2)
            
        else:
            print("¡LÍNEA PERDIDA!")
            cv2.putText(roi_bgr, "BUSCANDO PISTA", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # 3. DEBUGGING VISUAL (Líneas fijas de referencia)
        # Línea central ideal (Azul)
        cv2.line(roi_bgr, (centro_imagen, 0), (centro_imagen, 240), (255, 0, 0), 2)
        # Líneas de margen de tolerancia (Verdes)
        cv2.line(roi_bgr, (centro_imagen - margen, 0), (centro_imagen - margen, 240), (0, 255, 0), 1)
        cv2.line(roi_bgr, (centro_imagen + margen, 0), (centro_imagen + margen, 240), (0, 255, 0), 1)

        cv2.imshow('Camara F1 (ROI)', roi_bgr)
        cv2.imshow('Mascara (ROI)', mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    picam2.stop()
    cv2.destroyAllWindows()