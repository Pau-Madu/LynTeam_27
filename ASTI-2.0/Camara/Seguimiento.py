import cv2
import numpy as np
from picamera2 import Picamera2

# Inicializar la cámara con la librería nativa
picam2 = Picamera2()

# Forzar la resolución a 640x480 para un procesamiento rapidísimo
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# Valores fijos de calibración (S Max a 50 y V Min a 78)
lower_bound = np.array([0, 0, 78])
upper_bound = np.array([179, 50, 255])

print("Iniciando seguimiento de línea...")
print("Presiona 'q' en la ventana de vídeo para detener el coche.")

try:
    while True:
        # Capturar el fotograma directamente
        frame = picam2.capture_array()

        # Convertir de RGB a HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        # Crear la máscara con los valores calibrados
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        # Para poder dibujar elementos encima de la imagen a color, la pasamos a BGR
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Calcular el centro de gravedad (centroide) de la línea blanca
        momentos = cv2.moments(mask)
        
        # Evitar el error de división por cero si la cámara pierde la línea
        if momentos["m00"] > 0:
            # Calcular las coordenadas X e Y del centro de la línea
            cx = int(momentos["m10"] / momentos["m00"])
            cy = int(momentos["m01"] / momentos["m00"])

            # Dibujar un círculo rojo en el centro detectado para verlo en pantalla
            cv2.circle(frame_bgr, (cx, cy), 10, (0, 0, 255), -1)

            # Lógica de dirección básica
            # Como la imagen tiene 640px de ancho, el centro exacto está en X = 320
            centro_imagen = 320
            margen = 40 # Píxeles de tolerancia para considerar que el coche va recto

            if cx < (centro_imagen - margen):
                direccion = "GIRAR IZQUIERDA <-"
                color_texto = (0, 165, 255) # Naranja
            elif cx > (centro_imagen + margen):
                direccion = "GIRAR DERECHA ->"
                color_texto = (0, 165, 255) # Naranja
            else:
                direccion = "^^ RECTO ^^"
                color_texto = (0, 255, 0) # Verde

            # Imprimir la acción por terminal y pintarla en la pantalla
            print(f"Posición línea: {cx}px | Acción volante: {direccion}")
            cv2.putText(frame_bgr, direccion, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color_texto, 2)
            
        else:
            print("¡LÍNEA PERDIDA! Buscando...")
            cv2.putText(frame_bgr, "BUSCANDO PISTA", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Mostrar las ventanas de control
        cv2.imshow('Camara F1', frame_bgr)
        cv2.imshow('Mascara Binaria', mask)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    picam2.stop()
    cv2.destroyAllWindows()
