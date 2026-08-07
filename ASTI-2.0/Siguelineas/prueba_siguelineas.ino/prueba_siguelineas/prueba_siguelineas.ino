#include "sensores.h"

void setup() {
  Serial.begin(115200);
  delay(1000); 

  Serial.println("==================================");
  Serial.println("   Calibracion de 8 Sensores Siguelíneas");
  Serial.println("==================================");

  ejecutarCalibracion();
}

void loop() {
  bool valores[NUM_SENSORES] = {0};
  
  procesarLecturas(valores); // Llenamos el array pasándolo por referencia
  imprimirDebug(valores);    // Imprimimos de forma limpia
  
  delay(100);
}

