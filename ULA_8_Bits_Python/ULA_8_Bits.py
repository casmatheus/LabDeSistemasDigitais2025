import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import warnings

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
warnings.filterwarnings('ignore', category=UserWarning, module='pygame.pkgdata')
import pygame


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


class ALU_8bit:
    """
    Operações da ULA:

    - 000 (0): AND
    - 001 (1): OR
    - 010 (2): NOT (aplicado na entrada Y)
    - 011 (3): XOR
    - 100 (4): ADD (Soma)
    - 101 (5): SUB (Subtração)
    - 110 (6): MUL (Multiplicação)
    - 111 (7): DIV (Divisão inteira)
    """

    # --- Definição dos Opcodes ---
    OP_AND = 0b000
    OP_OR  = 0b001
    OP_NOT = 0b010
    OP_XOR = 0b011
    OP_ADD = 0b100
    OP_SUB = 0b101
    OP_MUL = 0b110
    OP_DIV = 0b111

    def __init__(self):
        """Inicializa a ULA."""
        self.MASK = 0xFF  # (binário: 11111111)

    def execute(self, X: int, Y: int, opcode: int):
        """
        Executa uma operação da ULA.
        Retorna: tuple (resultado, flag)
        """
        X = X & self.MASK
        Y = Y & self.MASK
        result = 0
        flag = 0

        if opcode == self.OP_AND:
            result = X & Y
            flag = 0
        elif opcode == self.OP_OR:
            result = X | Y
            flag = 0
        elif opcode == self.OP_NOT:
            result = (~Y) & self.MASK
            flag = 0
        elif opcode == self.OP_XOR:
            result = X ^ Y
            flag = 0
        elif opcode == self.OP_ADD:
            temp_sum = X + Y
            result = temp_sum & self.MASK
            flag = 1 if temp_sum > self.MASK else 0 # Flag = Carry Out
        elif opcode == self.OP_SUB:
            result = (X - Y) & self.MASK
            flag = 1 if X < Y else 0 # Flag = Borrow
        elif opcode == self.OP_MUL:
            temp_mul = X * Y
            result = temp_mul & self.MASK
            flag = 1 if temp_mul > self.MASK else 0 # Flag = Overflow
        elif opcode == self.OP_DIV:
            if Y == 0:
                result = 0 
                flag = 1   # Flag indica erro de divisão por zero
            else:
                result = (X // Y) & self.MASK 
                flag = 0
        else:
            print(f"Erro: Opcode {opcode} inválido.", file=sys.stderr)
            flag = 1 # Flag de erro geral

        return result, flag

#
# --- CLASSE DA INTERFACE GRÁFICA (GUI) ---
#
class AluGUI:
    def __init__(self, root):
        """Inicializa a interface gráfica."""
        
        self.audioFila = []
        self.tocandoAudio = False

        self.root = root
        self.root.title("Simulador ULA 8-bits")
        #icon = tk.PhotoImage(file='ULA.png')
        #root.iconphoto(True, icon)
        self.root.minsize(512, 270)
        self.root.resizable(True, True)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)


        # Instancia a ULA
        self.alu = ALU_8bit()

        self.tocarAudio('BemVindo.mp3')

        # Mapeamento de operações para o dropdown
        self.op_map = {
            "0: And": self.alu.OP_AND,
            "1: Or":  self.alu.OP_OR,
            "2: Not (em Y)": self.alu.OP_NOT,
            "3: Xor": self.alu.OP_XOR,
            "4: Adição": self.alu.OP_ADD,
            "5: Subtração": self.alu.OP_SUB,
            "6: Multiplicação": self.alu.OP_MUL,
            "7: Divisão": self.alu.OP_DIV
        }
        self.x = 0
        self.y = 0

        style = ttk.Style()
        
        # Define um tamanho de fonte padrão
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

        # --- Seção de Entradas ---
        row += 1
        larguraEntrada = 10
        input_frame = ttk.LabelFrame(main_frame, text="Entradas", padding="10", labelanchor='n')
        input_frame.grid(row=row, column=0, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Entrada X (8 Bits):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.x_entry = ttk.Entry(input_frame, width=larguraEntrada)
        self.x_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.x_entry.insert(0, f"{0:08b}")
        self.x = tk.StringVar(value="(Decimal: 0)")
        self.x_entry.bind("<FocusOut>", self.atualizarStringsDasCaixas)
        ttk.Label(input_frame, textvariable=self.x).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)


        ttk.Label(input_frame, text="Entrada Y (8 Bits):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.y_entry = ttk.Entry(input_frame, width=larguraEntrada)
        self.y_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.y_entry.insert(0, f"{0:08b}")
        self.y = tk.StringVar(value="(Decimal: 0)")
        self.y_entry.bind("<FocusOut>", self.atualizarStringsDasCaixas)
        ttk.Label(input_frame, textvariable=self.y).grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        ttk.Label(input_frame, text="Operação:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.op_combo = ttk.Combobox(input_frame, values=list(self.op_map.keys()), state="readonly", width=15)
        self.op_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.op_combo.current(0)
        self.comboStr = tk.StringVar(value=f"({0:03b})")
        self.op_combo.bind("<FocusOut>", self.atualizarStringsDasCaixas)
        ttk.Label(input_frame, textvariable=self.comboStr).grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)


        # --- Botão de Execução ---
        row += 1
        self.execute_button = ttk.Button(main_frame, text="Executar Operação", command=self.calcular)
        self.execute_button.grid(row=row, column=0, padx=5, pady=10)

        # --- Seção de Saídas ---
        row += 1
        output_frame = ttk.LabelFrame(main_frame, text="Saídas", padding="10", labelanchor='n')
        output_frame.grid(row=row, column=0, padx=5, pady=5)

        # Variáveis para atualizar os labels de resultado
        self.z_dec_var = tk.StringVar(value="Decimal: -")
        self.z_hex_var = tk.StringVar(value="Hex: -")
        self.z_bin_var = tk.StringVar(value="Binário: -")
        self.flag_var = tk.StringVar(value="Flag: -")

        ttk.Label(output_frame, textvariable=self.z_dec_var, style="Result.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(output_frame, textvariable=self.z_hex_var, style="Result.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(output_frame, textvariable=self.z_bin_var, style="Result.TLabel").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(output_frame, textvariable=self.flag_var, style="Result.TLabel").grid(row=3, column=0, padx=5, pady=10, sticky=tk.W)

        self.tocarAudio("insiraEntrada.mp3")
    
    def atualizarStringsDasCaixas(self, event):
        self.receberEAtualizarEntradas()
        return
    

    def receberEAtualizarEntradas(self):
        """Valida, formata e atualiza os campos de entrada X e Y."""
        
        try:
            x_str = self.x_entry.get()
            x = int(x_str, 2)
            if not (0 <= x <= 255): # Garante que está no range de 8 bits
                x = 0 # Reseta se for inválido (ex: "111111111")
        except ValueError:
            x = 0 # Reseta se for inválido (ex: "110a11")
        
        # Formata de volta para 8 bits e atualiza a caixa de entrada
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, f"{x:08b}")
        self.x.set(f"(Decimal: {x})") # Atualiza o label decimal

        # --- Processar Y ---
        try:
            y_str = self.y_entry.get()
            y = int(y_str, 2) # Tenta converter de binário
            if not (0 <= y <= 255):
                y = 0
        except ValueError:
            y = 0
        
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, f"{y:08b}")
        self.y.set(f"(Decimal: {y})")

        op_nome = self.op_combo.get()
        opcode = self.op_map[op_nome]
        self.comboStr.set(f"({opcode:03b})")

        return (x, y, opcode)

    def tocarAudio(self, path):
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


    def calcular(self):
        """Pega as entradas, executa a ULA e atualiza as saídas."""

        try:
            x, y, opcode = self.receberEAtualizarEntradas()

            # 2. Executar a ULA
            Z, F = self.alu.execute(x, y, opcode)

            # 3. Atualizar as Saídas
            self.z_dec_var.set(f"Decimal: {Z}")
            self.z_hex_var.set(f"Hex:     0x{Z:02X}")
            self.z_bin_var.set(f"Binário: {Z:08b}")
            
            # 4. Atualizar a Flag
            flag_nome = "Flag"
            if opcode == self.alu.OP_ADD and F == 1: flag_nome = "Carry"
            elif opcode == self.alu.OP_SUB and F == 1: flag_nome = "Borrow"
            elif opcode == self.alu.OP_MUL and F == 1: flag_nome = "Overflow"
            elif opcode == self.alu.OP_DIV and F == 1: flag_nome = "Div por Zero"
            
            self.flag_var.set(f"Flag ({flag_nome}): {F}")

        except ValueError:
            messagebox.showerror("Erro de Entrada", "As entradas X e Y devem ser números inteiros.")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")

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

        with open("UFRJascii.txt", "r", encoding="utf-8") as f:
            banner = f.read()
            print(banner)
        

