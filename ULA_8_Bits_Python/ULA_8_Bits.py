import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import warnings
import pyfirmata2 as pyfirmata
import time

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
warnings.filterwarnings('ignore', category=UserWarning, module='pygame.pkgdata')
import pygame


HABILITAR_AUDIO = 1

OP_AND = 0b000
OP_OR  = 0b001
OP_NOT = 0b010
OP_XOR = 0b011
OP_ADD = 0b100
OP_SUB = 0b101
OP_MUL = 0b110
OP_DIV = 0b111

def inputLoop(msg, tipo=str, min_v=None, max_v=None):
    while (1):
        entrada = input(msg).strip()
        
        if (not entrada):
            print("Erro, entrada vazia. Tente novamente.\n")
            continue
        
        try:
            entrada = tipo(entrada)
        except ValueError:
            print(f"Erro, entrada deve ser do tipo {tipo.__name__}. Tente novamente.\n")
            continue
        
        if ((min_v is not None) and (entrada < min_v)):
            print(f"Entrada deve ser maior ou igual a {min_v}. Tente novamente.\n")
            continue
        if ((max_v is not None) and (entrada > max_v)):
            print(f"Entrada deve ser menor ou igual a {max_v}. Tente novamente.\n")
            continue
        
        return entrada


# Pede para o usuário escolher um item em uma lista
def inputEscolha(msg, lista):
    for i, item in enumerate(lista):
        print(f"{i + 1}) {item}")

    i_escolhido = inputLoop(msg, tipo=int, min_v=1, max_v=len(lista)) - 1
    item_escolhido = lista[i_escolhido]

    return item_escolhido 


def op2str(A, B, opcode):
    if opcode == OP_AND:
        return f"{A} & {B}"
    elif opcode == OP_OR:
        return f"{A} | {B}"
    elif opcode == OP_NOT:
        return f"~{B}"
    elif opcode == OP_XOR:
        return f"{A} xor {B}"
    elif opcode == OP_ADD:
        return f"{A} + {B}"
    elif opcode == OP_SUB:
        return f"{A} - {B}"
    elif opcode == OP_MUL:
        return f"{A} * {B}"
    elif opcode == OP_DIV:
        return f"{A} / {B}"
    else:
        return ""

class Arduino:
    """
    Classe que define a comunicação com a Arduino
    """
    
    PORT = "COM3"
    pinoBotao = 8
    pinoLedCout = 13
    pinoLedZ3 = 9
    pinoLedZ2 = 10
    pinoLedZ1 = 11
    pinoLedZ0 = 12
    

    def __init__(self, root = None):
        """
        Inicializa Comunicação
        """
    
        self.root = root
        self.callbackBotao = None
        self.estadoAnteriorBotao = True # Solto

        self.erro = 0
        self.desabilitar = 0

        try:
            self.board = pyfirmata.Arduino(self.PORT)
        
            self.it = pyfirmata.util.Iterator(self.board)
            self.it.start()
            
            # Digital : Numero Do Pino : Input 
            self.botao = self.board.get_pin(f"d:{self.pinoBotao}:i")
            self.botao.mode = pyfirmata.INPUT_PULLUP
            self.botao.enable_reporting()
            
            # Digital : Numero do Pino : Output
            self.ledCout = self.board.get_pin(f"d:{self.pinoLedCout}:o")
            self.led3 = self.board.get_pin(f"d:{self.pinoLedZ3}:o")
            self.led2 = self.board.get_pin(f"d:{self.pinoLedZ2}:o")
            self.led1 = self.board.get_pin(f"d:{self.pinoLedZ1}:o")
            self.led0 = self.board.get_pin(f"d:{self.pinoLedZ0}:o")

        except pyfirmata.serial.SerialException as e:
            print(f"Erro, não foi possível se conectar ao port {self.PORT}. {e}")
            self.erro = 1
            self.desabilitar = 1

    def relacionarComBotaoGUI(self, callback):
        """
        Faz a relação entre um botão físico e uma função
        OBS: Funciona somente na aplicação Gráfica
        """

        if self.desabilitar == 1:
            return

        self.callbackBotao = callback
        self.esperarBotaoEmLoop()

    def esperarBotaoEmLoop(self):
        """ Loop interno para Espera do botão, (não chamar diretamente) """

        try:
            estadoAtual = self.botao.value

            if estadoAtual is None:
                self.root.after(50, self.esperarBotaoEmLoop)
                return

            # Botão vai de solto para pressionado
            if self.estadoAnteriorBotao == True and estadoAtual == False:
                self.callbackBotao()

            self.estadoAnteriorBotao = estadoAtual

            self.root.after(50, self.esperarBotaoEmLoop)
        except Exception as e:
            print(f"Erro, não foi possível verificar botão: {e}")
            self.erro = 1
            self.desabilitar = 1


    def ligar4LEDs(self, valor):
            """
            Envia um valor de 4 bits para os 4 LEDs de dados.
            """
            if self.desabilitar == 1:
                return
                
            try:
                self.led0.write(valor & 1)
                self.led1.write((valor >> 1) & 1)
                self.led2.write((valor >> 2) & 1)
                self.led3.write((valor >> 3) & 1)
                
            except Exception as e:
                print(f"Erro ao acender LEDs: {e}")
                self.erro = 1
                self.desabilitar = 1


    def mostrarResultadoEmLEDsGUI(self, saida, flag):
        """
        Mostra um resultado de 8 bits em 2 partes nos LEDs,
        Com espera de 1 segundo, sem bloquear a interface gráfica.
        """
        if self.desabilitar == 1:
            return

        try:
            self.ledCout.write(flag)

            parteBaixa = saida & 0x0F
            parteAlta = (saida >> 4) & 0x0F

            self.ligar4LEDs(parteBaixa)

            self.root.after(1000, self.ligar4LEDs, parteAlta)

        except Exception as e:
            print(f"Erro ao mostrar resultado nos LEDs: {e}")
            self.erro = 1
            self.desabilitar = 1


class ALU_8bit:
    """
    Operações da ULA:

    - 000 (0): AND
    - 001 (1): OR
    - 010 (2): NOT (aplicado na entrada B)
    - 011 (3): XOR
    - 100 (4): ADD (Soma)
    - 101 (5): SUB (Subtração)
    - 110 (6): MUL (Multiplicação)
    - 111 (7): DIV (Divisão inteira)
    """

    def __init__(self):
        """Inicializa a ULA."""
        self.MASK = 0xFF


    def execute(self, X: int, Y: int, opcode: int):
        """
        Executa uma operação da ULA.
        Retorna: tuple (resultado, flag)
        """
        X = X & self.MASK
        Y = Y & self.MASK
        result = 0
        flag = 0

        if opcode == OP_AND:
            result = X & Y
            flag = 0
        elif opcode == OP_OR:
            result = X | Y
            flag = 0
        elif opcode == OP_NOT:
            result = (~Y) & self.MASK
            flag = 0
        elif opcode == OP_XOR:
            result = X ^ Y
            flag = 0
        elif opcode == OP_ADD:
            temp_sum = X + Y
            result = temp_sum & self.MASK
            flag = 1 if temp_sum > self.MASK else 0 # Flag = Carry Out
        elif opcode == OP_SUB:
            result = (X - Y) & self.MASK
            flag = 1 if X < Y else 0 # Flag = Borrow
        elif opcode == OP_MUL:
            temp_mul = X * Y
            result = temp_mul & self.MASK
            flag = 1 if temp_mul > self.MASK else 0 # Flag = Overflow
        elif opcode == OP_DIV:
            if Y == 0:
                result = 0 
                flag = 1   # Flag indica erro de divisão por zero
            else:
                result = (X // Y) & self.MASK 
                flag = 0
        else:
            flag = 1 # Flag de erro geral

        return result, flag

#
# --- CLASSE DA INTERFACE GRÁFICA (GUI) ---
#
class AluGUI:

    MODO_MANUAL = '1'
    MODO_AUTOMATICO = '2'

    def __init__(self, root):
        """Inicializa a interface gráfica."""
        
        self.audioFila = []
        self.tocandoAudio = False

        self.root = root
        self.root.title("Simulador ULA 8-bits")
        self.root.minsize(512, 270)
        self.root.resizable(True, True)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.attributes('-topmost', True)

        # Instancia a ULA e Comunicação com Arduino
        self.alu = ALU_8bit()

        self.arduino = Arduino(root)
        if not self.arduino.erro:
            self.arduino.relacionarComBotaoGUI(self.calcular)

        self.tocarAudio('BemVindo.mp3')
        
        self.modo = tk.StringVar(value=self.MODO_MANUAL)


        # Mapeamento de operações para o dropdown
        self.op_map = {
            "000: And": OP_AND,
            "001: Or":  OP_OR,
            "010: Not (em B)": OP_NOT,
            "011: Xor": OP_XOR,
            "100: Adição": OP_ADD,
            "101: Subtração": OP_SUB,
            "110: Multiplicação": OP_MUL,
            "111: Divisão": OP_DIV
        }

        self.x = 0
        self.y = 0
        self.z = 0
        self.opcode = 0
        self.etapaAutomatica = 0

        style = ttk.Style()
        default_font_size = 10 
        default_font = ("Helvetica", default_font_size)
        self.root.option_add('*TCombobox*Listbox.font', default_font)



        style.configure(".", font=default_font) # '.' aplica a todos
        style.configure("TButton", font=default_font)
        style.configure("TLabel", font=default_font)
        style.configure("TEntry", font=default_font)
        style.configure("TCombobox", font=default_font)
        
        style.configure("TLabelframe", font=(default_font[0], default_font_size + 1, "bold"))
        style.configure("TLabelframe.Label", font=(default_font[0], default_font_size + 1, "bold"))

        style.configure("Result.TLabel", font=("Courier", default_font_size + 2))

        font_titulo = style.lookup("TLabelframe.Label", "font")

        # Cor de destaque azul claro
        COR_DESTAQUE_FUNDO = "#E0E8FF" 
        # Cor de destaque azul escuro (para o texto)
        COR_DESTAQUE_TEXTO = "#0000CC" 

        # 2. Configura o novo estilo de destaque
        style.configure(
            "Highlight.TLabelframe",
            labelanchor='n',
            background=COR_DESTAQUE_FUNDO  # <-- Muda o fundo do frame
        )
        style.configure(
            "Highlight.TLabelframe.Label",
            font=font_titulo,
            foreground=COR_DESTAQUE_TEXTO, # <-- Muda o texto
            background=COR_DESTAQUE_FUNDO  # <-- Muda o fundo do label (para combinar)
        )

        # --- Cria o frame principal ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)

        # --- Banner ---
        img = Image.open('BannerUFRJ.png')
        new_width = int(img.width * 0.65)
        new_height = int(img.height * 0.65)
        new_size = (new_width, new_height)
        img = img.resize(new_size, Image.Resampling.LANCZOS)

        self.banner_photo = ImageTk.PhotoImage(img)
        banner_label = ttk.Label(main_frame, image=self.banner_photo)
        row = 0
        banner_label.grid(row=row, column=0, pady=(0, 0))

        # --- Separador ---
        row += 1
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=row, column=0, sticky='ew', pady=5)

        # --- Ecolha de MODO ---
        row += 1
        self.mode_frame = ttk.LabelFrame(main_frame, text="Modo de Operação", padding="10", labelanchor='n')
        self.mode_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Radiobutton(self.mode_frame, text="Modo Manual", variable=self.modo, 
                        value=self.MODO_MANUAL, command=self.atualizarBotoesEntrada).pack(side=tk.LEFT, padx=50)
        ttk.Radiobutton(self.mode_frame, text="Modo Automático", variable=self.modo, 
                        value=self.MODO_AUTOMATICO, command=self.atualizarBotoesEntrada).pack(side=tk.RIGHT, padx=50)

        # --- Seção de Entradas ---
        row += 1
        larguraEntrada = 10
        self.input_frame = ttk.LabelFrame(main_frame, text="Entradas", padding="10", labelanchor='n')
        self.input_frame.grid(row=row, column=0, padx=5, pady=5)
        
        ttk.Label(self.input_frame, text="Entrada A (8 Bits):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.x_entry = ttk.Entry(self.input_frame, width=larguraEntrada)
        self.x_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.x_entry.insert(0, f"{0:08b}")
        self.xString = tk.StringVar(value="(Decimal: 0)")
        self.x_entry.bind("<FocusOut>", self.atualizarStringsDasCaixas)
        ttk.Label(self.input_frame, textvariable=self.xString).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)


        ttk.Label(self.input_frame, text="Entrada B (8 Bits):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.y_entry = ttk.Entry(self.input_frame, width=larguraEntrada)
        self.y_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.y_entry.insert(0, f"{0:08b}")
        self.yString = tk.StringVar(value="(Decimal: 0)")
        self.y_entry.bind("<FocusOut>", self.atualizarStringsDasCaixas)
        ttk.Label(self.input_frame, textvariable=self.yString).grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self.input_frame, text="Operação:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.op_combo = ttk.Combobox(self.input_frame, values=list(self.op_map.keys()), state="readonly", width=15)
        self.op_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.op_combo.current(0)
        self.comboStr = tk.StringVar(value=f"({0:03b})")
        self.op_combo.bind("<FocusOut>", self.atualizarStringsDasCaixas)
        ttk.Label(self.input_frame, textvariable=self.comboStr).grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)


        # --- Botão de Execução ---
        row += 1
        self.execute_button = ttk.Button(main_frame, text="Executar Operação", command=self.calcular)
        self.execute_button.grid(row=row, column=0, padx=5, pady=10)

        # --- Seção de Saídas ---
        row += 1
        self.output_frame = ttk.LabelFrame(main_frame, text="Saídas", padding="10", labelanchor='n')
        self.output_frame.grid(row=row, column=0, padx=5, pady=5)

        # Variáveis para atualizar os labels de resultado
        self.z_op_var  = tk.StringVar(value="Operação: -")
        self.z_dec_var = tk.StringVar(value="Decimal: -")
        self.z_hex_var = tk.StringVar(value="Hex: -")
        self.z_bin_var = tk.StringVar(value="Binário: -")
        self.flag_var  = tk.StringVar(value="Flag: -")

        ttk.Label(self.output_frame, textvariable=self.z_op_var, style="Result.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.output_frame, textvariable=self.z_dec_var, style="Result.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.output_frame, textvariable=self.z_hex_var, style="Result.TLabel").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.output_frame, textvariable=self.z_bin_var, style="Result.TLabel").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.output_frame, textvariable=self.flag_var, style="Result.TLabel").grid(row=4, column=0, padx=5, pady=10, sticky=tk.W)

        # self.tocarAudio("insiraEntrada.mp3")
    
    def highlightSaida(self):
        """ Aplica o estilo de destaque ao frame de saída. """
        try:
            self.output_frame.config(style="Highlight.TLabelframe")
            
            self.root.after(1500, self.unhighlightSaida)
            
        except tk.TclError:
            pass

    def unhighlightSaida(self):
        """ Restaura o estilo padrão do frame de saída. """
        try:
            self.output_frame.config(style="TLabelframe")
        except tk.TclError:
            pass


    def atualizarBotoesEntrada(self):
        """
        Habilita ou desabilita botoões da entrada baseado no modo 
        """
        modoAtual = self.modo.get()
    
        if modoAtual == self.MODO_AUTOMATICO:
            estadoNovo = "disabled"
            self.tocarAudio("ModoAuto.mp3")

        else:
            estadoNovo = "normal"
            self.tocarAudio("ModoManual.mp3")
    
        # Loop que passa por todos os botões da entrada
        for widget in self.input_frame.winfo_children():
            try:
                widget.config(state=estadoNovo)
            except tk.TclError:
                pass


    def atualizarStringsDasCaixas(self, event):
        self.receberEAtualizarEntradas()
        return

    def receberEAtualizarEntradas(self):
        """Valida, formata e atualiza os campos de entrada A, B e Operação."""
        
        try:
            x_str = self.x_entry.get()
            x = int(x_str, 2)
            if not (0 <= x <= 255): # Garante que está no range de 8 bits
                x = 0 # Reseta se for inválido (ex: "111111111")
        except ValueError:
            x = 0 # Reseta se for inválido (ex: "110a11")
        
        self.x = x
        
        # --- Processar B ---
        try:
            y_str = self.y_entry.get()
            y = int(y_str, 2) # Tenta converter de binário
            if not (0 <= y <= 255):
                y = 0
        except ValueError:
            y = 0
        
        self.y = y

        op_nome = self.op_combo.get()
        self.opcode = self.op_map[op_nome]

        self.setarEntradas()

        return (self.x, self.y, self.opcode)

    def setarEntradas(self):
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, f"{self.x:08b}")
        self.xString.set(f"(Decimal: {self.x})")

        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, f"{self.y:08b}")
        self.yString.set(f"(Decimal: {self.y})")

        self.comboStr.set(f"({self.opcode:03b})")

        return


    def tocarAudio(self, path):
        if HABILITAR_AUDIO == 0:
            return

        self.audioFila.append(path)
        
        if not self.tocandoAudio:
            self.processarFilaDeAudio()

    def processarFilaDeAudio(self):
        if not self.audioFila:
            self.is_playing_audio = False
            return
        
        if self.tocandoAudio:
            return

        self.tocandoAudio = True
        path = self.audioFila.pop(0)
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.audioTerminado()


    def audioTerminado(self):
        if pygame.mixer.music.get_busy():
            self.root.after(100, self.audioTerminado)
        else:
            self.tocandoAudio = False
            self.processarFilaDeAudio()

    def atualizarSaida(self, op1, op2, opcode):
        op_str = op2str(op1, op2, opcode)
        self.z_op_var.set(f"R = {op_str}")
        self.z_dec_var.set(f"Decimal: {self.z}")
        self.z_hex_var.set(f"Hex:     0x{self.z:02X}")
        self.z_bin_var.set(f"Binário: {self.z:08b}")
        
        F = self.flag
        flag_nome = "Flag"
        if opcode == OP_ADD and F == 1: flag_nome = "Carry"
        elif opcode == OP_SUB and F == 1: flag_nome = "Borrow"
        elif opcode == OP_MUL and F == 1: flag_nome = "Overflow"
        elif opcode == OP_DIV and F == 1: flag_nome = "Div por Zero"

        self.flag_var.set(f"Flag ({flag_nome}): {self.flag}")

        self.arduino.mostrarResultadoEmLEDsGUI(self.z, self.flag)

    def calcular(self):
        """Pega as entradas, executa a ULA e atualiza as saídas."""

        modo = self.modo.get()
        if modo == self.MODO_MANUAL:
            try:
                # Ler Entrada
                self.x, self.y, self.opcode = self.receberEAtualizarEntradas()

                # Executar ALU 
                self.z, self.flag = self.alu.execute(self.x, self.y, self.opcode)

                # Mostrar Saida 
                self.atualizarSaida('A', 'B', self.opcode)

            except ValueError:
                messagebox.showerror("Erro de Entrada", "As entradas A e B devem ser números inteiros.")
            except Exception as e:
                print(e)
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")

        elif modo == self.MODO_AUTOMATICO:
            etapa = self.etapaAutomatica
            self.x = 0b00000001
            self.y = 0b00000010
            if etapa == 0:
                self.z, self.flag = self.alu.execute(self.x, self.y, OP_ADD)
                self.atualizarSaida('A', 'B', OP_ADD)
            elif etapa == 1:
                self.z, self.flag = self.alu.execute(self.z, self.z, OP_MUL)
                self.atualizarSaida('R', 'R', OP_MUL)
            elif etapa == 2:
                self.z, self.flag = self.alu.execute(self.z, self.y, OP_SUB)
                self.atualizarSaida('R', 'B', OP_SUB)
            elif etapa == 3:
                self.z, self.flag = self.alu.execute(self.z, self.x, OP_SUB)
                self.atualizarSaida('R', 'A', OP_SUB)
            elif etapa == 4:
                self.z, self.flag = self.alu.execute(self.z, self.y, OP_DIV)
                self.atualizarSaida('R', 'B', OP_DIV)
            elif etapa == 5:
                self.z, self.flag = self.alu.execute(self.z, self.x, OP_AND)
                self.atualizarSaida('R', 'A', OP_AND)
            elif etapa == 6:
                self.z, self.flag = self.alu.execute(self.z, self.z, OP_NOT)
                self.atualizarSaida('R', 'R', OP_NOT)
            elif etapa == 7:
                self.z, self.flag = self.alu.execute(self.z, self.x, OP_OR)
                self.atualizarSaida('R', 'A', OP_OR)
            elif etapa == 8:
                self.z, self.flag = self.alu.execute(self.z, self.x, OP_ADD)
                self.atualizarSaida('R', 'A', OP_ADD)
            elif etapa == 9:
                 self.z, self.flag = self.alu.execute(self.z, self.z, OP_NOT)
                 self.atualizarSaida('R', 'R', OP_NOT)
                 self.etapaAutomatica = -1
                 self.tocarAudio("ResultadoFinal.mp3")
                 self.highlightSaida()

            self.etapaAutomatica += 1


def interfaceTerminal():
    with open("UFRJascii.txt", "r", encoding="utf-8") as f:
        banner = f.read()
        print(banner)

if __name__ == "__main__":

    print("")
    escolha = inputEscolha("Escolha o tipo de Interface: ",
                            ["Gráfica", "Terminal"])

    if (escolha == "Gráfica"):
        # Inicia o modulo de audio
        pygame.mixer.init()

        # Inicia a aplicação gráfica
        root = tk.Tk()
        app = AluGUI(root)
        root.mainloop()
    elif (escolha == "Terminal"):
        interfaceTerminal()


