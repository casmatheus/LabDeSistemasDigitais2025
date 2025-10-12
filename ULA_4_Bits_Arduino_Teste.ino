/*ULA 4 BITS
 - entradas X e Y (4 bits)
 - saida: Z (Z3 Z2 Z1 Z0) e Cout (1 bit)
 -operações:
  - 000: AND ; 001: 0R ; 010: NOT ; 011: XOR ; 100:Soma com Cout (cin = 0) 
  101:subtrator ; 110: multiplicador ; 111: divisor (parte inteira de X/Y)
*/

// Configura a necessidade de uso do botao 
//#define BUTTON

// Modos de Operacao
#define MANUAL 1
#define AUTOMATICO 2

// Operacoes
#define AND 0b000
#define OR  0b001
#define NOT 0b010
#define XOR 0b011
#define SUM 0b100
#define SUB 0b101
#define MUL 0b110
#define DIV 0b111

// Tamanho do Buffer de Entrada
#define inputBufferSize 6

//Definindo os pinos do arduino
#define ledCout 13
#define ledZ3 9
#define ledZ2 10
#define ledZ1 11
#define ledZ0 12
#ifdef BUTTON
#define button = 8;
#endif

//Definindo as funcoes das operacoes, para o compilador saber que existem
byte andOp(byte A, byte B);
byte orOp(byte A, byte B);
byte notOp(byte B);
byte xorOp(byte A, byte B);
byte somador(byte A, byte B, byte &Cout);
byte subtrator(byte A, byte B, byte &BorrowOut);
byte multiplicador(byte A, byte B,byte &OV);
byte divisor(byte A, byte B);
byte receberEntrada(char nomeDaEntrada, char* entradaString);
byte receberOperacao(char* entradaString);
byte str2byte(char* str);
byte str2dec(char* str);
void readSerialInput(char* buffer, int bufferSize);
void printarResultado(byte resultado, byte cout, byte operacao);
void modoManual(void);
void modoAutomatico(void);

#ifdef BUTTON
void waitButton(void);
#endif

void setup() {
  Serial.begin(9600);

	#ifdef BUTTON
  pinMode(button,  INPUT_PULLUP);
	#endif  
	
	pinMode(ledCout, OUTPUT);
  pinMode(ledZ3,   OUTPUT);
  pinMode(ledZ2,   OUTPUT);
  pinMode(ledZ1,   OUTPUT);
  pinMode(ledZ0,   OUTPUT);

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
	char entradaString[inputBufferSize] = {};
	
	Serial.print("\nSelecione o modo:\n  (1) Manual\n  (2) Automático\n");

	readSerialInput(entradaString, inputBufferSize);

	#ifdef BUTTON
  waitButton();
	#endif

	byte modo = str2dec(entradaString);
	if (modo == MANUAL) {
		modoManual();

	} else if (modo == AUTOMATICO) {
		modoAutomatico();	
	} 

}

//Implementacao das operacoes em funcoes separadas

byte andOp(byte A, byte B){
  return A & B;
}

byte orOp(byte A, byte B){
  return (byte)(A | B);
}

byte notOp(byte B){
  return ~B & 0x0F;
}

byte xorOp(byte A, byte B){
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
  return (byte)A / B;
} 

void acenderLeds(byte valor, byte cout ){
  digitalWrite(ledZ3, bitRead(valor,3)); //ledZ3 recebe o valor do MSB (3o bit de Z)
  digitalWrite(ledZ2, bitRead(valor,2));
  digitalWrite(ledZ1, bitRead(valor,1));
  digitalWrite(ledZ0, bitRead(valor,0));
  digitalWrite(ledCout, cout); //ledCout recebe o valor de cout (0 ou 1)
}

byte str2byte(char* str) {
  return (byte)strtol(str, NULL, 2);
}

byte str2dec(char* str) {
  return (byte)strtol(str, NULL, 10);
}


byte receberEntrada(char nomeDaEntrada, char* entradaString) {	
	byte entradaByte = 0;

  Serial.print("Digite a entrada ");
	Serial.print(nomeDaEntrada);
	Serial.println(" com 4 bits:");
  
	readSerialInput(entradaString, inputBufferSize);
  entradaByte = str2byte(entradaString);

	#ifdef BUTTON
  waitButton();
	#endif

	Serial.print(nomeDaEntrada);
  Serial.print(" = ");
  Serial.print(entradaByte);
  Serial.print(" | ");
  Serial.println(entradaString);
	
	return entradaByte;
}

byte receberOperacao(char* entradaString) {	
	byte operacaoByte = 0;

  Serial.print("Escolha a operacao: ");

	readSerialInput(entradaString, inputBufferSize);
  operacaoByte = str2byte(entradaString);

	#ifdef BUTTON
  waitButton();
	#endif

	return operacaoByte;
}

void readSerialInput(char* buffer, int bufferSize) {
  int index = 0;
  while (true) {
    if (Serial.available() > 0) {
      char c = Serial.read();
      if (c == '\n' || c == '\r') {
        buffer[index] = '\0';

        while (Serial.available() > 0) Serial.read();
        return;
      } else if (index < bufferSize - 1) {
        buffer[index++] = c;
      }
    }
  }
}

#ifdef BUTTON
void waitButton(void) {
  Serial.println("Aperte o Botão para carregar a entrada!");
  byte dotCount = 0;
  while (digitalRead(button) == HIGH) {
    Serial.print(".");
    delay(500);
    dotCount++;
    if (dotCount > 3) {
      Serial.print("\r\r\r"); 
      dotCount = 0;
    }
  }
}
#endif

void printarResultado(byte resultado, byte cout, byte operacao) {
  Serial.print("Binário: ");
  Serial.print(cout);
  Serial.print(bitRead(resultado,3));
  Serial.print(bitRead(resultado,2));
  Serial.print(bitRead(resultado,1));
  Serial.print(bitRead(resultado,0));
  Serial.print(" | ");
  Serial.print("Decimal: ");
  if (cout == 1) {
    Serial.print(resultado + 16);
  } else {
    Serial.print(resultado);
  }

  if (cout == 1) {
    Serial.print(" | ");
    if (operacao == SUM) Serial.print("Teve Cout");
    else if (operacao == SUB) Serial.print("Teve Borrow");
    else if (operacao == MUL)
      Serial.print("Teve Overflow");
    }
}


void modoAutomatico(void) {
	char entradaString[inputBufferSize] = {};
	byte cout = 0;	

	byte entradaA = receberEntrada('A', entradaString);
	byte entradaB = receberEntrada('B', entradaString);
	
	byte resultadoR = somador(entradaA, entradaB, cout);
	Serial.print("\n");
	Serial.print("R = A + B = ");
	printarResultado(resultadoR, cout, SUM);
	
	resultadoR = multiplicador(resultadoR, resultadoR, cout);	
	Serial.print("\n");
	Serial.print("R = R * R = ");          	
	printarResultado(resultadoR, cout, MUL);

	resultadoR = subtrator(resultadoR, entradaB, cout);	
	Serial.print("\n");
	Serial.print("R = R - B = ");          	
	printarResultado(resultadoR, cout, SUB);

	resultadoR = subtrator(resultadoR, entradaA, cout);	
	Serial.print("\n");
	Serial.print("R = R - A = ");          	
  printarResultado(resultadoR, cout, SUB);

	resultadoR = divisor(resultadoR, entradaB);	
	Serial.print("\n");
	Serial.print("R = R / B = ");          	
  printarResultado(resultadoR, 0, DIV);

	resultadoR = andOp(resultadoR, entradaA);	
	Serial.print("\n");
	Serial.print("R = R & A = ");          	
	printarResultado(resultadoR, 0, AND);

	resultadoR = notOp(resultadoR);	
	Serial.print("\n");
	Serial.print("R = ~R = ");          	
	printarResultado(resultadoR, 0, NOT);

	resultadoR = orOp(resultadoR, entradaA);	
	Serial.print("\n");
	Serial.print("R = R | A = ");          	
	printarResultado(resultadoR, 0, OR);

	resultadoR = somador(resultadoR, entradaA, cout);
	Serial.print("\n");
	Serial.print("R = R + A = ");
	printarResultado(resultadoR, cout, SUM);

	resultadoR = notOp(resultadoR);	
	Serial.print("\n");
	Serial.print("R = ~R = ");          	
	printarResultado(resultadoR, 0, NOT);
}

void modoManual(void) {

	char entradaString[inputBufferSize] = {};

	byte entradaX = receberEntrada('X', entradaString);
	byte entradaY = receberEntrada('Y', entradaString);

  Serial.println(F("\t\t\t\t\t╔═══════════════════ PAINEL DE OPERAÇÕES DA ULA ═══════════════════╗"));
  Serial.println(F("\t\t\t\t\t║  ╔═══════════╗  ╔══════════╗  ╔════════════╗  ╔═══════════════╗  ║"));
  Serial.println(F("\t\t\t\t\t║  ║ 000: AND  ║  ║ 010: NOT ║  ║ 100: SOMA  ║  ║ 110: MULTIPL. ║  ║"));
  Serial.println(F("\t\t\t\t\t║  ╚═══════════╝  ╚══════════╝  ╚════════════╝  ╚═══════════════╝  ║"));
  Serial.println(F("\t\t\t\t\t║  ╔═══════════╗  ╔══════════╗  ╔════════════╗  ╔═══════════════╗  ║"));
  Serial.println(F("\t\t\t\t\t║  ║ 001: OR   ║  ║ 011: XOR ║  ║ 101: SUB.  ║  ║ 111: DIVISAO  ║  ║"));
  Serial.println(F("\t\t\t\t\t║  ╚═══════════╝  ╚══════════╝  ╚════════════╝  ╚═══════════════╝  ║"));
  Serial.println(F("\t\t\t\t\t╚══════════════════════════════════════════════════════════════════╝"));
  Serial.println("");

	byte operacao = receberOperacao(entradaString);

  const char* op;
	byte saidaZ = 0;
	byte Cout = 0;

  switch(operacao) {
    case AND: {
      op = "And";
      saidaZ = andOp(entradaX,entradaY);
    } break;

    case OR: {
      op = "Or";
      saidaZ = orOp(entradaX,entradaY);
    } break;

    case NOT: {
      op = "Not";
      saidaZ = notOp(entradaY);
    } break;

    case XOR: {
      op = "Xor";
      saidaZ = xorOp(entradaX,entradaY);
    }  break;

    case SUM: {
      op = "Soma";
      saidaZ = somador(entradaX,entradaY, Cout);
    }  break;

    case SUB: {
      op = "Sub";
      saidaZ = subtrator(entradaX,entradaY, Cout);
    }  break;

    case MUL: {
      op = "Mul";
      saidaZ = multiplicador(entradaX,entradaY,Cout);
    }  break;

    case DIV: {
      op = "Div";
      saidaZ = divisor(entradaX,entradaY);
    }  break;

    default:
      Serial.println("Operacao invalida!");
      return;
  }

  Serial.print("Operação: ");
  Serial.print(entradaString);
  Serial.print(" | ");
  Serial.print(op);
  Serial.print("\n");

	//Exibindo resultado no monitor -> resultado: Cout Z3 Z2 Z1 Z0
  Serial.println("Resultado:");
	printarResultado(saidaZ, Cout, operacao);
	
  acenderLeds(saidaZ, Cout);

	Serial.println("");
	Serial.println("");
}
