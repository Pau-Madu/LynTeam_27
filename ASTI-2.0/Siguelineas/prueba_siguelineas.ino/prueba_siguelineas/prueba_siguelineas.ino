// Definimos los pines del ESP32-S3 donde conectaste cada sensor (S1 a S8)
// NOTA: Puedes cambiar estos números si usas otros pines GPIO de tu tarjeta.
const int PINES_SENSORES[8] = {4,5,6,7,15,16,17,18};

void setup() {
  // Iniciamos la comunicación serie para ver los datos en la pantalla
  Serial.begin(115200);
  delay(1000); // Pequeña pausa para establecer conexión

  Serial.println("==================================");
  Serial.println("   Prueba de 8 Sensores Siguelíneas");
  Serial.println("==================================");

  // Configurar cada pin como entrada
  for (int i = 0; i < 8; i++) {
    pinMode(PINES_SENSORES[i], INPUT);
  }
}

void loop() {
  Serial.print("Lecturas [S1 ... S8]: ");

  // Leemos el estado de cada uno de los 8 sensores
  for (int i = 0; i < 8; i++) {
    int estado = analogRead(PINES_SENSORES[i]);
    
    // Imprimimos el resultado de cada sensor
    Serial.print(estado);
    Serial.print(" ");
  }
  
  // Salto de línea
  Serial.println();

  // Pausa ligera para que las lecturas en el monitor serie se puedan leer con calma
  delay(200);
}