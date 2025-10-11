/*ULA 4 BITS
 - entradas X e Y (4 bits)
 - saida: Z (Z3 Z2 Z1 Z0) e Cout (1 bit)
 -operações:
  - 000: AND ; 001: 0R ; 010: NOT ; 011: XOR ; 100:Soma com Cout (cin = 0) 
  101:subtrator ; 110: multiplicador ; 111: divisor (parte inteira de X/Y)
*/

// Definicao das variaveis de entrada e saida
byte entradaX;
byte entradaY;
byte operacao;
byte saidaZ;
byte Cout;


//Definindo os pinos do arduino
const int ledCout = 13;
const int ledZ3 = 9;
const int ledZ2 = 10;
const int ledZ1 = 11;
const int ledZ0 = 12;
const int button = 8;

//Definindo as funcoes das operacoes, para o compilador saber que existem
byte AND(byte A, byte B);
byte OR(byte A, byte B);
byte NOT(byte B);
byte XOR(byte A, byte B);
byte somador(byte A, byte B, byte &Cout);
byte subtrator(byte A, byte B, byte &BorrowOut);
byte multiplicador(byte A, byte B,byte &OV);
byte divisor(byte A, byte B);
byte str2byte(String str);
void waitButton(void);

void setup() {
  Serial.begin(9600);
  pinMode(button,  INPUT_PULLUP);
  pinMode(ledCout, OUTPUT);
  pinMode(ledZ3,   OUTPUT);
  pinMode(ledZ2,   OUTPUT);
  pinMode(ledZ1,   OUTPUT);
  pinMode(ledZ0,   OUTPUT);

/*
  Serial.println("");
  Serial.println("================== Funcionamento da ULA 4 BITS ==================");
  Serial.print("- Recebe as entradas X e Y, respectivamente, por meio do monitor serial (Obs: entradas de 4 bits)\n");
  Serial.print("- Recebe a operação desejada, também por meio do monitor (Obs:entrada de 3 bits)\n");
  Serial.print("- Retorna o resultado da operacao em binario e em decimal: Cout Z3 Z2 Z1 Z0\n");
*/

  Serial.println("");
  Serial.println(F("\t\t\t\t\t╔═══════════════════════════════════════════════════╗"));
  Serial.println(F("\t\t\t\t\t║   .------------------------------------------.    ║"));
  Serial.println(F("\t\t\t\t\t║   |   ░▒▓ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+- ▓▒░  |   ║"));
  Serial.println(F("\t\t\t\t\t║   |   ░▒▓ | ULA 4BITS - SERIAL MONITOR | ▓▒░  |   ║"));
  Serial.println(F("\t\t\t\t\t║   |   ░▒▓ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+- ▓▒░  |   ║"));
  Serial.println(F("\t\t\t\t\t║   |   ░▒▓ >>> PROCESSADOR DE 4 BITS <<<  ▓▒░  |   ║"));
  Serial.println(F("\t\t\t\t\t║   '------------------------------------------'    ║"));
  Serial.println(F("\t\t\t\t\t╚═══════════════════════════════════════════════════╝"));
}

void loop() {
  Cout = 0;
  Serial.println("");

  String entradaXstring;

  Serial.println("Digite a entrada X com 4 bits: ");
  while (Serial.available() == 0) {
  }
  entradaXstring = Serial.readStringUntil('\n');
  entradaX = str2byte(entradaXstring);//recebe o valor digitado no serial monitor
  waitButton();

  Serial.print("\n");
  Serial.print("X = ");
  Serial.print(entradaX);
  Serial.print(" | ");
  Serial.print(entradaXstring);
  Serial.print("\n");

  while (Serial.available() > 0) {
    Serial.read(); // Lê e descarta qualquer caractere restante (como o '\n')
  }

  Serial.println("Digite a entrada Y com 4 bits: ");
  while (Serial.available() == 0) {
  }
  String entradaYstring = Serial.readStringUntil('\n');
  entradaY = str2byte(entradaYstring);
  waitButton();

  Serial.print("\n");
  Serial.print("Y = ");
  Serial.print(entradaY);
  Serial.print(" | ");
  Serial.print(entradaYstring);
  Serial.print("\n");

  while (Serial.available() > 0) {
    Serial.read(); // Lê e descarta qualquer caractere restante (como o '\n')
  }

  /*
  Serial.println("Digite a operacao desejada: ");
  Serial.print("000: AND ; 001: OR ; 010: NOT ; 011: XOR\n");
  Serial.print("100: SOMA ; 101: SUBTRACAO ; 110: MULTIPLICACAO ; 111: DIVISAO (apenas parte inteira)\n");
  */

  Serial.println("");
  Serial.println("================== PAINEL DE OPERAÇÕES DA ULA ==================");
  Serial.println("");
  Serial.println(" .-----------.  .----------.      .------------.  .---------------.");
  Serial.println(" | 000: AND  |  | 010: NOT |      | 100: SOMA  |  | 110: MULTIPL. |");
  Serial.println(" '-----------'  '----------'      '------------'  '---------------'");
  Serial.println(" .----------.  .----------.      .------------.  .---------------.");
  Serial.println(" | 001: OR   |  | 011: XOR |      | 101: SUB.  |  | 111: DIVISAO  |");
  Serial.println(" '----------'  '----------'      '------------'  '---------------'");
  Serial.println("");
  Serial.println("================================================================");
  Serial.print("\n> Escolha a operacao: ");

  while (Serial.available() == 0) {
  }
  String entradaOp = Serial.readStringUntil('\n');
  operacao = str2byte(entradaOp);

  while (Serial.available() > 0) {
    Serial.read(); // Lê e descarta qualquer caractere restante (como o '\n')
  }
  waitButton();
  Serial.print("\n");

  String op;
  //basicamente um if...else para realizar a operacao devida
  switch(operacao) {
    case 0b000:
      op = "and";
      saidaZ = AND(entradaX,entradaY);
      break;
    case 0b001:
      op = "or";
      saidaZ = OR(entradaX,entradaY);
      break;
    case 0b010:
      op = "not";
      saidaZ = NOT(entradaY);
      break;
    case 0b011:
      op = "xor";
      saidaZ = XOR(entradaX,entradaY);
      break;
    case 0b100:
      op = "soma";
      saidaZ = somador(entradaX,entradaY, Cout);
      break;
    case 0b101:
      op = "sub";
      saidaZ = subtrator(entradaX,entradaY, Cout);
      break;
    case 0b110:
      op = "mul";
      saidaZ = multiplicador(entradaX,entradaY,Cout);
      break;
    case 0b111:
      op = "div";
      saidaZ = divisor(entradaX,entradaY);
      break;
    default:
      return;
  }

  Serial.print("Operação: ");
  Serial.print(entradaOp);
  Serial.print(" | ");
  Serial.print(op);
  Serial.print("\n");

//Exibindo resultado no monitor -> resultado: Cout Z3 Z2 Z1 Z0
  Serial.println("Resultado:");
  Serial.print("Binário: ");
  Serial.print(Cout);
  Serial.print(bitRead(saidaZ,3));
  Serial.print(bitRead(saidaZ,2));
  Serial.print(bitRead(saidaZ,1));
  Serial.print(bitRead(saidaZ,0));
  Serial.print(" | ");
  Serial.print("Decimal: ");
  if (Cout == 1) {
    Serial.print(saidaZ + 16);
  } else {
    Serial.print(saidaZ);
  }

  if (Cout == 1) {
    Serial.print(" | ");
    if (operacao == 0b100)
      Serial.print("Teve Cout");
    else if (operacao == 0b101)
      Serial.print("Teve Borrow");
    else if (operacao == 0b110)
      Serial.print("Teve Overflow");
    }

//Exibindo resultado nos leds's
  acenderLeds(saidaZ, Cout);
}

//Implementacao das operacoes em funcoes separadas

byte AND(byte A, byte B){
  return A & B;
}

byte OR(byte A, byte B){
  return (byte)(A | B);
}

byte NOT(byte B){
  return ~B & 0xF;
}

byte XOR(byte A, byte B){
  return (byte)(A ^ B);
}

byte somador(byte A, byte B, byte &Cout){
  byte soma = A + B;

  Cout = soma > 0x0F;
  
  return (byte)(soma & 0x0F); //soma and "1111" -> retorna apenas os 4 bits (o outro fica em Cout, se tiver) 
}

byte subtrator (byte A, byte B, byte &BorrowOut){
  byte subtracao = A - B;
  
  BorrowOut = A < B;

  return (byte)(subtracao & 0x0F);  
}

byte multiplicador (byte A, byte B, byte &OV){
  byte multiplicacao = A*B;
  
  OV = multiplicacao > 0x0F; // Overflow se A*B > 15 
  
  return (byte)(multiplicacao & 0x0F);
}

byte divisor(byte A, byte B){
  return (byte)A/B; //operador / realiza divisão inteira
} 

//funcao para acender os leds
void acenderLeds(byte valor, byte cout ){
  digitalWrite(ledZ3, bitRead(valor,3)); //ledZ3 recebe o valor do MSB (3o bit de Z)
  digitalWrite(ledZ2, bitRead(valor,2));
  digitalWrite(ledZ1, bitRead(valor,1));
  digitalWrite(ledZ0, bitRead(valor,0));
  digitalWrite(ledCout, cout); //ledCout recebe o valor de cout (0 ou 1)
}

byte str2byte(String string) {
  return (byte)strtol(string.c_str(), NULL, 2);
}

void waitButton(void) {
  Serial.println("Aperte o Botão para carregar a entrada!");
  byte dotCount = 0;
  while (digitalRead(button) == HIGH) {
    Serial.print(".");
    delay(500);
    dotCount++;
    if (dotCount > 3) {
      Serial.print("\r"); 
      dotCount = 0;
    }
  }
}
