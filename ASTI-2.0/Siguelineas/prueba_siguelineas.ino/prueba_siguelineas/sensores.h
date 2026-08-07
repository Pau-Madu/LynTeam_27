#ifndef SENSORES_H
#define SENSORES_H

#include <Arduino.h>

// Constantes globales de configuración
const int NUM_SENSORES = 8;
const int VALOR_MAX_ADC = 4095;
const int PINES_SENSORES[NUM_SENSORES] = {4, 5, 6, 15, 16, 17, 18, 8};

// Arrays globales para almacenar la calibración
extern int maximos[NUM_SENSORES];
extern int minimos[NUM_SENSORES];

// Declaración de funciones
int realizarLectura(int posicion);
bool verificarSensoresFuncionales();
void ejecutarCalibracion();
void procesarLecturas(bool *resultado);
void imprimirDebug(bool *valoresActuales);

#endif
