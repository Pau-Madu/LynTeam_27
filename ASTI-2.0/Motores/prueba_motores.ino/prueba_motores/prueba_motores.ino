// ==========================================
// CONFIGURACIÓN DE PINES
// ==========================================
const int IN1 = 4; // Control Driver DRV8871 (GPIO 4)
const int IN2 = 5; // Control Driver DRV8871 (GPIO 5)

const int ENCODER_A = 6; // Canal A del Encoder (Cable Amarillo)
const int ENCODER_B = 7; // Canal B del Encoder (Cable Blanco)

const int PWM_MAX = 180; // Limite seguro para motor de 12V con LiPo 4S

volatile long contadorPulsos = 0;

void IRAM_ATTR contarPulso() {
  if (digitalRead(ENCODER_B) == HIGH) {
    contadorPulsos++;
  } else {
    contadorPulsos--;
  }
}

void setup() {
  // EL BROWNOUT SE MANTIENE ACTIVADO POR DEFECTO EN EL SISTEMA
  Serial.begin(115200);
  delay(1000); 

  Serial.println("\n==========================================");
  Serial.println("  PRUEBA CON PROTECCIÓN BROWNOUT ACTIVA");
  Serial.println("==========================================");

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  
  // Borrado de registros PWM
  analogWrite(IN1, 0);
  analogWrite(IN2, 0);

  pinMode(ENCODER_A, INPUT_PULLUP);
  pinMode(ENCODER_B, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(ENCODER_A), contarPulso, RISING);

  Serial.println("-> Interrupción activada en GPIO 6");
  Serial.println("-> Sistema de protección contra caídas de tensión: ACTIVO");
  Serial.println("-> Iniciando secuencia...\n");
}

void loop() {
  // ----------------------------------------
  // PASO 1: Giro Hacia Adelante (Rampa Suave)
  // ----------------------------------------
  Serial.println("[1/4] Girando ADELANTE (Aceleración Progresiva)...");
  contadorPulsos = 0; 
  analogWrite(IN2, 0); 

  // Rampa de aceleración: Pasa de 0 a 180 progresivamente en 300ms
  // Esto evita el pico de demanda de corriente (Inrush Current)
  for (int pwm = 10; pwm <= PWM_MAX; pwm += 5) {
    analogWrite(IN1, pwm);
    delay(10);
  }
  
  delay(2000); // 2 segundos a velocidad constante
  
  Serial.print("   └─ Pulsos contados: ");
  Serial.println(contadorPulsos);

  // ----------------------------------------
  // PASO 2: Parada
  // ----------------------------------------
  Serial.println("[2/4] FRENANDO...");
  analogWrite(IN1, 0); 
  analogWrite(IN2, 0);
  delay(1000);

  // ----------------------------------------
  // PASO 3: Giro Hacia Atrás (Rampa Suave)
  // ----------------------------------------
  Serial.println("[3/4] Girando ATRÁS (Aceleración Progresiva)...");
  contadorPulsos = 0;
  analogWrite(IN1, 0); 

  for (int pwm = 10; pwm <= PWM_MAX; pwm += 5) {
    analogWrite(IN2, pwm);
    delay(10);
  }

  delay(2000); 

  Serial.print("   └─ Pulsos contados: ");
  Serial.println(contadorPulsos);

  // ----------------------------------------
  // PASO 4: Parada y pausa
  // ----------------------------------------
  Serial.println("[4/4] FRENANDO... Esperando 3s para reiniciar ciclo.\n");
  analogWrite(IN1, 0); 
  analogWrite(IN2, 0);
  delay(3000);
}