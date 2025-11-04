/*
 * Espera por comandos de 1 byte via Serial para enviar dados binários brutos.
 *
 * Comando 'G': Envia 32 bytes (Registradores de Propósito Geral) 
 * Comando 'I': Envia 224 bytes (Registradores de Entrada e Saída) 
 * Comando 'S': Envia 2048 bytes (SRAM)
 *
 */

#include <avr/io.h> // Para RAMEND

// Array global para armazenar os GPRs
uint8_t gpr_values[32];

void setup() {
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {

    char cmd = Serial.read();

		// Registradores de Propósito Geral
    if (cmd == 'G') {

      asm volatile (
        "st X+, r0 \n\t" "st X+, r1 \n\t" "st X+, r2 \n\t" "st X+, r3 \n\t"
        "st X+, r4 \n\t" "st X+, r5 \n\t" "st X+, r6 \n\t" "st X+, r7 \n\t"
        "st X+, r8 \n\t" "st X+, r9 \n\t" "st X+, r10 \n\t" "st X+, r11 \n\t"
        "st X+, r12 \n\t" "st X+, r13 \n\t" "st X+, r14 \n\t" "st X+, r15 \n\t"
        "st X+, r16 \n\t" "st X+, r17 \n\t" "st X+, r18 \n\t" "st X+, r19 \n\t"
        "st X+, r20 \n\t" "st X+, r21 \n\t" "st X+, r22 \n\t" "st X+, r23 \n\t"
        "st X+, r24 \n\t" "st X+, r25 \n\t" "st X+, r26 \n\t" "st X+, r27 \n\t"
        "st X+, r28 \n\t" "st X+, r29 \n\t" "st X+, r30 \n\t" "st X+, r31 \n\t"
        : : [ptr] "x" (gpr_values) : "memory"
      );
      
      Serial.write(gpr_values, 32);
      Serial.flush();
    }

		// SRAM    
    if (cmd == 'S') {
      byte* sram_start = (byte*) 0x0100;
      uint16_t sram_size = 2048; 
      Serial.write(sram_start, sram_size);
      Serial.flush();
    }

    // Registradores de Entrada e Saída
    if (cmd == 'I') {

      byte* io_start = (byte*) 0x0020;
      uint16_t io_size = 224; // (0xFF - 0x20) + 1
      
      Serial.write(io_start, io_size);
      Serial.flush();
    }
  }
}
