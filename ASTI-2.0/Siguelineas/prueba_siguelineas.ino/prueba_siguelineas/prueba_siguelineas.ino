const int PINES_SENSORES[8] = {4, 5, 6, 15, 16, 17, 18, 8};
int maximos[8];
int minimos[8];
bool primerIntento = true; // Cambiado por un booleano más claro
int matchCount = 0;

void setup() {
  Serial.begin(115200);
  delay(1000); 

  Serial.println("==================================");
  Serial.println("   Calibracion de 8 Sensores Siguelíneas");
  Serial.println("==================================");

  for (int i = 0; i < 8; i++) {
    pinMode(PINES_SENSORES[i], INPUT);
  }
  do {
    // 1. CORRECCIÓN: Control de mensajes por pantalla
    if (primerIntento) {
      Serial.println("Calibrando... Mueve el robot sobre blanco");
      primerIntento = false;
    } else {
      Serial.println("Fallo detectado (Sensores saturados). Recalibrando en 2 segundos...");
      delay(2000); // Pausa para que el usuario pueda reacomodar el robot si es necesario
    }

    // 2. CORRECCIÓN: Resetear arrays en cada intento de calibración
    for (int i = 0; i < 8; i++) {
      maximos[i] = 0;
      minimos[i] = 4095; // 4095 es el máximo valor analógico en ESP32
    }

    // Bucle de lectura de sensores
    for (int contador = 0; contador <= 100; contador++) {
      for (int i = 0; i < 8; i++) {
        int estado = analogRead(PINES_SENSORES[i]);
        
        // Ubicamos los máximos y los mínimos
        if (estado < minimos[i]) minimos[i] = estado;
        if (estado > maximos[i]) maximos[i] = estado;
      }
      delayMicroseconds(5000);
    }

    // 3. Conteo de sensores saturados
    matchCount = 0;
    for (int num = 0; num < 8; num++) {
      if (maximos[num] == 4095) {
        matchCount++;
      }
    }

    Serial.print("Sensores saturados detectados: ");
    Serial.println(matchCount);

  } while (matchCount == 8); // Se repite si los 8 sensores se quedaron bloqueados en 4095

  
  Serial.println("\n==================================");
  Serial.println("Calibración completada con éxito:");
  Serial.println("==================================");

  Serial.print("Mínimos: ");
  for (int k = 0; k < 8; k++) {
    Serial.print(minimos[k]);
    Serial.print(" ");
  }

  Serial.println();
  Serial.print("Máximos: ");
  for (int k = 0; k < 8; k++) {
    Serial.print(maximos[k]);
    Serial.print(" ");
  }
  Serial.println();
}

void loop() {
  bool valores[8] = {0,0,0,0,0,0,0,0};
  for (int i = 0; i < 8; i++) {
    int estado = analogRead(PINES_SENSORES[i]);
    if (estado > (maximos[i] + (maximos[i]-minimos[i])/100)) valores[i] = 1;
    else {valores[i] = 0;}
  }
  Serial.print("Valores actuales: ");
  Serial.println(" ");
  for (int j = 0; j < 8; j++){
    Serial.print(valores[j]);
    Serial.print(" ");
  }
  Serial.println();
  delay(100);
}