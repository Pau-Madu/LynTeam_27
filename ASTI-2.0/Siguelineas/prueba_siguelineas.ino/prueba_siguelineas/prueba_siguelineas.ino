// Definimos los pines del ESP32-S3 donde conectaste cada sensor (S1 a S8)
// NOTA: Puedes cambiar estos números si usas otros pines GPIO de tu tarjeta.
const int PINES_SENSORES[8] = {4,5,6,15,16,17,18,8};
int maximos[8] = {0,0,0,0,0,0,0,0};
int minimos[8] = {6000,6000,6000,6000,6000,6000,6000,6000};

void setup() {
  // Iniciamos la comunicación serie para ver los datos en la pantalla
  Serial.begin(115200);
  delay(1000); // Pequeña pausa para establecer conexión

  Serial.println("==================================");
  Serial.println("   Calibracion de 8 Sensores Siguelíneas");
  Serial.println("==================================");

  for (int i = 0; i < 8; i++) {
    pinMode(PINES_SENSORES[i], INPUT);

    for(int contador = 0; contador <= 100; contador++){
      for (int i = 0; i < 8; i++) {
        int estado = analogRead(PINES_SENSORES[i]);
        //Ubicamos los maximos y los minimos
        if (estado < minimos[i]) minimos[i] = estado;
        if (estado > maximos[i]) maximos[i] = estado;
      }
    delayMicroseconds(5000);
    }
  }

  
  Serial.print("Calibración completada:");

  Serial.println();
  Serial.print("Mínimos: ");
  for (int k = 0; k < 8; k++){
    Serial.print(minimos[k]);
    Serial.print(" ");
  }

  Serial.println();
  Serial.print("Maximos: ");
  for (int k = 0; k < 8; k++){
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