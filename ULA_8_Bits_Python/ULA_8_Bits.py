import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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
        self.root = root
        self.root.title("Simulador ULA 8-bits")
        self.root.geometry("400x400")
        self.root.resizable(False, False)

        # Instancia a ULA
        self.alu = ALU_8bit()

        # Mapeamento de operações para o dropdown
        self.op_map = {
            "0: AND": self.alu.OP_AND,
            "1: OR":  self.alu.OP_OR,
            "2: NOT (em Y)": self.alu.OP_NOT,
            "3: XOR": self.alu.OP_XOR,
            "4: ADD": self.alu.OP_ADD,
            "5: SUB": self.alu.OP_SUB,
            "6: MUL": self.alu.OP_MUL,
            "7: DIV": self.alu.OP_DIV
        }

        # --- Cria o frame principal ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Seção de Entradas ---
        input_frame = ttk.LabelFrame(main_frame, text="Entradas", padding="10")
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(input_frame, text="Entrada X (0-255):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.x_entry = ttk.Entry(input_frame, width=10)
        self.x_entry.grid(row=0, column=1, padx=5, pady=5)
        self.x_entry.insert(0, "0")

        ttk.Label(input_frame, text="Entrada Y (0-255):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.y_entry = ttk.Entry(input_frame, width=10)
        self.y_entry.grid(row=1, column=1, padx=5, pady=5)
        self.y_entry.insert(0, "0")

        ttk.Label(input_frame, text="Operação:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.op_combo = ttk.Combobox(input_frame, values=list(self.op_map.keys()), state="readonly", width=15)
        self.op_combo.grid(row=2, column=1, padx=5, pady=5)
        self.op_combo.current(0) # Define "AND" como padrão

        # --- Botão de Execução ---
        self.execute_button = ttk.Button(main_frame, text="Executar Operação", command=self.calcular)
        self.execute_button.grid(row=1, column=0, padx=5, pady=10)

        # --- Seção de Saídas ---
        output_frame = ttk.LabelFrame(main_frame, text="Saídas", padding="10")
        output_frame.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Variáveis para atualizar os labels de resultado
        self.z_dec_var = tk.StringVar(value="Decimal: -")
        self.z_hex_var = tk.StringVar(value="Hex: -")
        self.z_bin_var = tk.StringVar(value="Binário: -")
        self.flag_var = tk.StringVar(value="Flag: -")

        style = ttk.Style()
        style.configure("Result.TLabel", font=("Courier", 12))

        ttk.Label(output_frame, textvariable=self.z_dec_var, style="Result.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(output_frame, textvariable=self.z_hex_var, style="Result.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(output_frame, textvariable=self.z_bin_var, style="Result.TLabel").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(output_frame, textvariable=self.flag_var, style="Result.TLabel").grid(row=3, column=0, padx=5, pady=10, sticky=tk.W)

    def calcular(self):
        """Pega as entradas, executa a ULA e atualiza as saídas."""
        try:
            # 1. Obter e validar entradas
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            
            if not (0 <= x <= 255 and 0 <= y <= 255):
                messagebox.showerror("Erro de Entrada", "As entradas X e Y devem estar entre 0 e 255.")
                return

            op_nome = self.op_combo.get()
            opcode = self.op_map[op_nome]

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
    # Inicia a aplicação gráfica
    root = tk.Tk()
    app = AluGUI(root)
    root.mainloop()
