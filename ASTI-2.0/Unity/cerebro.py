import cv2
import numpy as np
import threading
import time
from flask import Flask, Response
from picamera2 import Picamera2

# ==========================================
# IMPORTAMOS TUS NUEVOS MÓDULOS MODULARES
# ==========================================
import siguelineas
import sumo

app = Flask(__name__)

# ==========================================
# VARIABLES GLOBALES (La Máquina de Estados)
# ==========================================
estado_actual = "STANDBY" 
ultimo_frame_bgr = None

# ==========================================
# 1. RUTAS DEL SERVIDOR WEB (Escucha a Unity)
# ==========================================
@app.route('/shot.jpg')
def get_shot():
    global ultimo_frame_bgr
    if ultimo_frame_bgr is not None:
        ret, buffer = cv2.imencode('.jpg', ultimo_frame_bgr)
        return Response(buffer.tobytes(), mimetype='image/jpeg')
    return "No hay imagen", 404

@app.route('/modo_siguelineas')
def set_modo_siguelineas():
    global estado_actual
    estado_actual = "SIGUELINEAS"
    print("\n>>> [UNITY] Orden recibida: MODO SIGUELÍNEAS ACTIVADO")
    return "Modo Siguelineas Activado", 200

@app.route('/modo_sumo')
def set_modo_sumo():
    global estado_actual
    estado_actual = "SUMO"
    print("\n>>> [UNITY] Orden recibida: MODO SUMO ACTIVADO")
    return "Modo Sumo Activado", 200

@app.route('/standby')
def set_standby():
    global estado_actual
    estado_actual = "STANDBY"
    print("\n>>> [UNITY] Orden recibida: MODO STANDBY (Punto muerto)")
    return "Standby activado", 200

@app.route('/stop')
def emergency_stop():
    global estado_actual
    estado_actual = "STOP"
    print("\n>>> [UNITY] ¡¡¡PARADA DE EMERGENCIA ACTIVADA!!!")
    return "Emergencia activada", 200

def iniciar_servidor_web():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ==========================================
# 2. CONTROL FÍSICO DEL ROBOT
# ==========================================
def detener_motores():
    print("[MOTOR] Motores clavados a 0.")

# ==========================================
# 3. BUCLE PRINCIPAL (El corazón del programa)
# ==========================================
def main():
    global ultimo_frame_bgr, estado_actual
    estado_anterior = "STANDBY"
    
    # 1. Arrancamos el servidor web
    hilo_web = threading.Thread(target=iniciar_servidor_web)
    hilo_web.daemon = True
    hilo_web.start()
    
    # 2. Inicializamos la cámara a la resolución unificada (320x240)
    print("Iniciando cámara a máxima velocidad (320x240)...")
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (320, 240)})
    picam2.configure(config)
    picam2.start()
    
    print("======================================")
    print(" CEREBRO LISTO. ESPERANDO A UNITY... ")
    print("======================================")
    
    try:
        while True:
            # Capturamos la foto
            frame = picam2.capture_array()
            ultimo_frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Limpiamos ventanas si cambiamos de modo en Unity
            if estado_actual != estado_anterior:
                cv2.destroyAllWindows()
                estado_anterior = estado_actual
            
            # --- MÁQUINA DE ESTADOS ---
            if estado_actual == "SIGUELINEAS":
                # Le pasamos el frame directo y activamos las ventanas locales
                error = siguelineas.procesar_vision(ultimo_frame_bgr, modo_debug=True)
                
            elif estado_actual == "SUMO":
                # Le pasamos el frame directo (ya no necesita resize) y activamos las ventanas locales
                accion, valor_giro = sumo.procesar_sumo(ultimo_frame_bgr, modo_debug=True)
                
            elif estado_actual == "STOP":
                detener_motores()
                estado_actual = "STANDBY" 
            
            elif estado_actual == "STANDBY":
                # En Standby no ejecutamos procesamiento pesado, solo mantenemos vivo el vídeo
                pass
            
            # Ligero respiro para la CPU
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nApagando cerebro...")
    finally:
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()