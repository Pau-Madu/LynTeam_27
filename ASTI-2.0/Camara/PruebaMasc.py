import cv2
import numpy as np

def nothing(x):
    pass

# Inicializar la cámara (cambia el 0 si tu cámara está en otro índice, o usa un vídeo)
cap = cv2.VideoCapture(0)

# Crear una ventana con controles deslizantes
cv2.namedWindow('Ajuste de Mascara')
cv2.createTrackbar('H Min', 'Ajuste de Mascara', 0, 179, nothing)
cv2.createTrackbar('S Min', 'Ajuste de Mascara', 0, 255, nothing)
cv2.createTrackbar('V Min', 'Ajuste de Mascara', 0, 255, nothing)
cv2.createTrackbar('H Max', 'Ajuste de Mascara', 179, 179, nothing)
cv2.createTrackbar('S Max', 'Ajuste de Mascara', 255, 255, nothing)
cv2.createTrackbar('V Max', 'Ajuste de Mascara', 255, 255, nothing)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. Convertir el frame de RGB a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 2. Leer los valores actuales de los deslizadores
    h_min = cv2.getTrackbarPos('H Min', 'Ajuste de Mascara')
    s_min = cv2.getTrackbarPos('S Min', 'Ajuste de Mascara')
    v_min = cv2.getTrackbarPos('V Min', 'Ajuste de Mascara')
    h_max = cv2.getTrackbarPos('H Max', 'Ajuste de Mascara')
    s_max = cv2.getTrackbarPos('S Max', 'Ajuste de Mascara')
    v_max = cv2.getTrackbarPos('V Max', 'Ajuste de Mascara')

    # 3. Definir los límites inferior y superior
    lower_bound = np.array([h_min, s_min, v_min])
    upper_bound = np.array([h_max, s_max, v_max])

    # 4. Crear la máscara
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # 5. Operación AND bit a bit para ver el color real filtrado (Opcional)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Mostrar las ventanas
    cv2.imshow('Frame Original', frame)
    cv2.imshow('Mascara Binaria', mask)
    cv2.imshow('Resultado', result)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()