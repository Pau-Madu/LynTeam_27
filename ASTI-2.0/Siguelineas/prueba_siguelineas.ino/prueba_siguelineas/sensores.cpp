#include "sensores.h"

int maximos[NUM_SENSORES];
int minimos[NUM_SENSORES];
bool primerIntento = true;

int realizarLectura(int posicion) {
  return analogRead(PINES_SENSORES[posicion]);
}

bool verificarSensoresFuncionales() {
  for (int i = 0; i < NUM_SENSORES; i++) {
    if (maximos[i] == VALOR_MAX_ADC) { 
      Serial.print("Se ha detectado un sensor saturado: ");
      Serial.print(i + 1);
      Serial.print(" en el pin ");
      Serial.println(PINES_SENSORES[i]);
      return false;   
    }
  }
  return true;
}

void ejecutarCalibracion() {
  for (int i = 0; i < NUM_SENSORES; i++) {
    pinMode(PINES_SENSORES[i], INPUT);
  }

  do {
    if (primerIntento) {
      Serial.println("Calibrando... Mueve el robot sobre blanco y negro");
      primerIntento = false;
    } else {
      Serial.println("Fallo detectado (Sensores saturados). Recalibrando en 2 segundos...");
      delay(2000); 
    }

    for (int i = 0; i < NUM_SENSORES; i++) {
      maximos[i] = 0;
      minimos[i] = VALOR_MAX_ADC;
    }

    for (int contador = 0; contador <= 100; contador++) {
      for (int i = 0; i < NUM_SENSORES; i++) {
        int estado = realizarLectura(i);
        if (estado < minimos[i]) minimos[i] = estado;
        if (estado > maximos[i]) maximos[i] = estado;
      }
      delayMicroseconds(5000);
    }
  } while (!verificarSensoresFuncionales()); 

  Serial.println("\n==================================");
  Serial.println("Calibración completada con éxito:");
  Serial.println("==================================");
}

void procesarLecturas(bool *resultado) {
  for (int i = 0; i < NUM_SENSORES; i++) {
    int estado = realizarLectura(i);
    int umbral = minimos[i] + ((maximos[i] - minimos[i]) / 2);
    resultado[i] = (estado > umbral) ? 1 : 0;
  }
}

void imprimirDebug(bool *valoresActuales) {
  Serial.print("Valores actuales: ");
  for (int j = 0; j < NUM_SENSORES; j++) {
    Serial.print(valoresActuales[j]);
    Serial.print(" ");
  }
  Serial.println();
}
