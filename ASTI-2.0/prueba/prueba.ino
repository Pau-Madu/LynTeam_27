const int PINES[8] = {4,5,6,7,15,16,17,18};

int minValores[8];
int maxValores[8];

// Función para leer un pin con promedio (elimina ruido eléctrico)
int leerFiltrado(int pin) {
  long suma = 0;
  for (int i = 0; i < 10; i++) {
    suma += analogRead(pin);
  }
  return suma / 10;
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  analogReadResolution(12);

  for (int i = 0; i < 8; i++) {
    minValores[i] = 4095;
    maxValores[i] = 0;
  }

  Serial.println("==========================================");
  Serial.println("   CALIBRANDO (6 SEGUNDOS)");
  Serial.println("   Mueve el sensor de izquierda a derecha");
  Serial.println("   sobre la LÍNEA NEGRA y el FONDO BLANCO.");
  Serial.println("==========================================");

  unsigned long tiempoInicio = millis();
  while (millis() - tiempoInicio < 6000) {
    for (int i = 0; i < 8; i++) {
      int lectura = leerFiltrado(PINES[i]);

      if (lectura < minValores[i]) minValores[i] = lectura;
      if (lectura > maxValores[i]) maxValores[i] = lectura;
    }
    delay(10);
  }

  // Protección anti-ruido: Si la diferencia min/max es muy pequeña, corregir
  for (int i = 0; i < 8; i++) {
    int delta = maxValores[i] - minValores[i];
    if (delta < 500) { // Si casi no cambió durante la calibración
      minValores[i] = 500;
      maxValores[i] = 3500;
    }
  }

  Serial.println("¡Calibración terminada!\n");
}

void loop() {
  Serial.print("Lectura [S1..S8]: ");

  for (int i = 0; i < 8; i++) {
    int raw = leerFiltrado(PINES[i]);

    // Mapeo invertido: Fondo Blanco = 0, Línea Negra = 1000
    int normalizado = map(raw, maxValores[i], minValores[i], 0, 1000);
    normalizado = constrain(normalizado, 0, 1000);

    Serial.print(normalizado);
    Serial.print("\t");
  }
  Serial.println();
  delay(150);
}