import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import warnings
import time
import dump

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

INDENT = "\t\t\t\t\t"

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

def receber_entrada_binario(nome_da_entrada, num_bits):
    """ Pede e valida uma entrada binária do usuário """
    prompt = f"{INDENT}Digite a entrada {nome_da_entrada} com {num_bits} bits: "
    while True:
        s = input(prompt).strip()
        if len(s) != num_bits:
            print(f"{INDENT}Erro: A entrada deve ter exatamente {num_bits} bits. Tente novamente.")
            continue
        if not all(c in '01' for c in s):
            print(f"{INDENT}Erro: A entrada deve conter apenas '0' e '1'. Tente novamente.")
            continue

        # Se chegou aqui, é válido
        valor_byte = int(s, 2)
        print(f"{INDENT}{nome_da_entrada} = {valor_byte} | {s}")
        print() # Espaçamento
        return valor_byte

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
    
def pegarNomeFlag(opcode, flag):
    """ Retorna o nome correto da flag (igual à GUI) """
    if flag == 0:
        return "Flag"  # Nome padrão
    if opcode == OP_ADD:
        return "Carry"
    if opcode == OP_SUB:
        return "Borrow"
    if opcode == OP_MUL:
        return "Overflow"
    if opcode == OP_DIV:
        return "Div por Zero"
    return "Flag"  # Nome padrão para flag=1 sem caso especial

def imprimir_na_caixa(op_str, resultado, flag, operacao, is_final=False):
    """
    Imprime a caixa de resultado formatada, estilo GUI.
    (Corrigido alinhamento do gradiente e largura do título)
    """
    # --- 1. PREPARAÇÃO DOS DADOS (Igual à GUI) ---
    flag_nome = pegarNomeFlag(operacao, flag)

    linhas = [
        f"Operação: {op_str}",
        f"Decimal : {resultado}",
        f"Hex     : 0x{resultado:02X}",
        f"Binário : {resultado:08b}",
        f"Flag ({flag_nome}): {flag}"
    ]

    titulo_final = ""
    if is_final:
        titulo_final = "R E S U L T A D O  F I N A L"

    # Encontrar a largura máxima necessária, considerando os dados E o título
    largura_caixa = 0
    # Primeiro, checa as linhas de dados
    for linha in linhas:
        if len(linha) > largura_caixa:
            largura_caixa = len(linha)
    
    # AGORA, checa também a linha do título
    if len(titulo_final) > largura_caixa:
        largura_caixa = len(titulo_final)
            
    # Adicionar um pequeno padding
    largura_caixa += 2 

    # --- 2. DESENHO DA CAIXA ---
    
    # Função auxiliar para formatar e imprimir uma linha
    def print_linha(texto, char_borda="║"):
        # Adiciona padding de espaços à direita
        padding = " " * (largura_caixa - len(texto)) 
        print(f"{INDENT}{char_borda} {texto}{padding} {char_borda}")

    char_topo_esq, char_topo, char_topo_dir = "╔", "═", "╗"
    char_fundo_esq, char_fundo, char_fundo_dir = "╚", "═", "╝"
    char_borda = "║"
    
    # Largura total da caixa, incluindo bordas
    largura_total_caixa = largura_caixa + 4

    if is_final:
        # --- CAIXA FINAL (com mais destaque) ---
        
        # Remove os espaços extras e usa a largura total calculada
        print(f"\n{INDENT}{'░' * largura_total_caixa}")
        
        # Centraliza o título
        padding_total = largura_caixa - len(titulo_final)
        padding_esq = padding_total // 2
        padding_dir = padding_total - padding_esq
        
        print(f"{INDENT}{char_topo_esq}{char_topo * (largura_caixa + 2)}{char_topo_dir}")
        print(f"{INDENT}{char_borda} {' ' * padding_esq}{titulo_final}{' ' * padding_dir} {char_borda}")
        
        char_meio_esq, char_meio, char_meio_dir = "╠", "═", "╣"
        print(f"{INDENT}{char_meio_esq}{char_meio * (largura_caixa + 2)}{char_meio_dir}")
        
    else:
        # --- CAIXA SIMPLES ---
        print(f"\n{INDENT}{char_topo_esq}{char_topo * (largura_caixa + 2)}{char_topo_dir}")


    # Imprime todas as linhas de dados (Operação, Dec, Hex, Bin, Flag)
    for linha in linhas:
        print_linha(linha, char_borda)

    # Imprime fundo da caixa
    print(f"{INDENT}{char_fundo_esq}{char_fundo * (largura_caixa + 2)}{char_fundo_dir}")
    
    if is_final:
        print(f"{INDENT}{'▒' * largura_total_caixa}")
        print()

def print_banner_setup():
    """ Imprime o banner inicial (copiado do seu C++) """
    print()
    print(INDENT + "╔═══════════════════════════════════════════════════╗")
    print(INDENT + "║   .------------------------------------------.    ║")
    print(INDENT + "║   |   ░▒▓ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+- ▓▒░  |   ║")
    print(INDENT + "║   |   ░▒▓ | ULA 8BITS - TERMINAL PYTHON |▓▒░  |   ║")
    print(INDENT + "║   |   ░▒▓ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+- ▓▒░  |   ║")
    print(INDENT + "║   |   ░▒▓ >>> PROCESSADOR DE 8 BITS <<<  ▓▒░  |   ║")
    print(INDENT + "║   '------------------------------------------'    ║")
    print(INDENT + "╚═══════════════════════════════════════════════════╝")

def print_menu_modo():
    """ Imprime a caixa de seleção de modo (copiado do seu C++) """
    print("\n")
    print(INDENT + "╔═════ ░▒▓  SELECIONE O MODO   ▓▒░ ═════╗")
    print(INDENT + "║                                       ║")
    print(INDENT + "║         (1) Modo Manual               ║")
    print(INDENT + "║         (2) Modo Automatico           ║")
    print(INDENT + "║                                       ║")
    print(INDENT + "╚═══════════════════════════════════════╝")
    print("\n")

def print_painel_operacoes():
    """ Imprime o painel de operações (copiado do seu C++) """
    print(INDENT + "╔═══════════════════ PAINEL DE OPERAÇÕES DA ULA ═══════════════════╗")
    print(INDENT + "║  ╔═══════════╗  ╔══════════╗  ╔════════════╗  ╔═══════════════╗  ║")
    print(INDENT + "║  ║ 000: AND  ║  ║ 010: NOT ║  ║ 100: SOMA  ║  ║ 110: MULTIPL. ║  ║")
    print(INDENT + "║  ╚═══════════╝  ╚══════════╝  ╚════════════╝  ╚═══════════════╝  ║")
    print(INDENT + "║  ╔═══════════╗  ╔══════════╗  ╔════════════╗  ╔═══════════════╗  ║")
    print(INDENT + "║  ║ 001: OR   ║  ║ 011: XOR ║  ║ 101: SUB.  ║  ║ 111: DIVISAO  ║  ║")
    print(INDENT + "║  ╚═══════════╝  ╚══════════╝  ╚════════════╝  ╚═══════════════╝  ║")
    print(INDENT + "╚══════════════════════════════════════════════════════════════════╝")
    print()

def modo_manual(alu):
    """ Executa a ULA no modo manual """
    
    # 1. Receber Entradas (8 bits)
    entrada_x = receber_entrada_binario('X', 8)
    entrada_y = receber_entrada_binario('Y', 8)

    # 2. Imprimir Painel
    print_painel_operacoes()

    # 3. Receber Operação (3 bits)
    operacao_str_prompt = f"{INDENT}Escolha a operacao (3 bits): "
    while True:
        s = input(operacao_str_prompt).strip()
        if len(s) != 3:
            print(f"{INDENT}Erro: A operação deve ter exatamente 3 bits. Tente novamente.")
            continue
        if not all(c in '01' for c in s):
            print(f"{INDENT}Erro: A operação deve conter apenas '0' e '1'. Tente novamente.")
            continue

        operacao = int(s, 2)
        break # Sai do loop se for válido
    
    # 4. Executar ULA
    saida_z, flag = alu.execute(entrada_x, entrada_y, operacao)

    # 5. Mapear opcode para nome (para o print)
    op_map = {
        0: "And", 1: "Or", 2: "Not", 3: "Xor",
        4: "Soma", 5: "Sub", 6: "Mul", 7: "Div"
    }
    op_nome = op_map.get(operacao, "Invalida")

    # 6. Imprimir caixa de operação
    print(f"\n{INDENT}╔═══════════════════════════════════════╗")
    print(f"{INDENT}║           O P E R A Ç Ã O             ║")
    print(f"{INDENT}╚═══════════════════════════════════════╝")
    print(f"{INDENT}{s} | {op_nome}")

    # 7. Criar string da operação (ex: "X + Y")
    op_str = ""
    if operacao == OP_NOT:
        op_str = f"~Y (~{entrada_y})"
    else:
        op_simbolos = {0: '&', 1: '|', 3: '^', 4: '+', 5: '-', 6: '*', 7: '/'}
        op_s = op_simbolos.get(operacao, '?')
        op_str = f"X {op_s} Y ({entrada_x} {op_s} {entrada_y})"

    # 8. Imprimir caixa de resultado final
    imprimir_na_caixa(op_str, saida_z, flag, operacao, is_final=True)

def modo_automatico(alu):
    """ 
    Executa a sequência de operações do modo automático 
    """
    
   # Receber Entradas Iniciais
    entrada_a = receber_entrada_binario('A', 8)
    entrada_b = receber_entrada_binario('B', 8)
    
    flag = 0
    resultado_r = 0

    # Sequência de Passos
    
    # R = A + B
    resultado_r, flag = alu.execute(entrada_a, entrada_b, OP_ADD)
    imprimir_na_caixa("A + B", resultado_r, flag, OP_ADD, is_final=False)
    
    # R = R * R
    resultado_r_anterior = resultado_r
    resultado_r, flag = alu.execute(resultado_r, resultado_r, OP_MUL)
    imprimir_na_caixa(f"R * R ({resultado_r_anterior} * {resultado_r_anterior})", resultado_r, flag, OP_MUL, is_final=False)

    # R = R - B
    resultado_r_anterior = resultado_r
    resultado_r, flag = alu.execute(resultado_r, entrada_b, OP_SUB)
    imprimir_na_caixa(f"R - B ({resultado_r_anterior} - {entrada_b})", resultado_r, flag, OP_SUB, is_final=False)

    # R = R - A
    resultado_r_anterior = resultado_r
    resultado_r, flag = alu.execute(resultado_r, entrada_a, OP_SUB)
    imprimir_na_caixa(f"R - A ({resultado_r_anterior} - {entrada_a})", resultado_r, flag, OP_SUB, is_final=False)

    # R = R / B
    resultado_r_anterior = resultado_r
    resultado_r, flag = alu.execute(resultado_r, entrada_b, OP_DIV)
    imprimir_na_caixa(f"R / B ({resultado_r_anterior} / {entrada_b})", resultado_r, flag, OP_DIV, is_final=False)

    # R = R & A
    resultado_r_anterior = resultado_r
    resultado_r, flag = alu.execute(resultado_r, entrada_a, OP_AND)
    imprimir_na_caixa(f"R & A ({resultado_r_anterior} & {entrada_a})", resultado_r, flag, OP_AND, is_final=False)

    # R = ~R
    resultado_r_anterior = resultado_r
    resultado_r, flag = alu.execute(0, resultado_r, OP_NOT) # X é irrelevante para NOT
    imprimir_na_caixa(f"~R (~{resultado_r_anterior})", resultado_r, flag, OP_NOT, is_final=False)

    # R = R | A
    resultado_r_anterior = resultado_r
    resultado_r, flag = alu.execute(resultado_r, entrada_a, OP_OR)
    imprimir_na_caixa(f"R | A ({resultado_r_anterior} | {entrada_a})", resultado_r, flag, OP_OR, is_final=False)

    # R = R + A
    resultado_r_anterior = resultado_r
    resultado_r, flag = alu.execute(resultado_r, entrada_a, OP_ADD)
    imprimir_na_caixa(f"R + A ({resultado_r_anterior} + {entrada_a})", resultado_r, flag, OP_ADD, is_final=False)

    # R = ~R (Final)
    resultado_r_anterior = resultado_r
    resultado_r, flag = alu.execute(0, resultado_r, OP_NOT)
    imprimir_na_caixa(f"~R (~{resultado_r_anterior})", resultado_r, flag, OP_NOT, is_final=True)

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

        # Instancia a ULA
        self.alu = ALU_8bit()

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
        img = Image.open('imagens/BannerUFRJ.png')
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

            self.x = 0b00000001
            self.y = 0b00000010
            self.setarEntradas()

            self.tocarAudio("ModoAuto.mp3")

        else:
            estadoNovo = "normal"

            self.x = 0
            self.y = 0
            self.op_combo.current(0) 
            self.opcode = self.op_map[self.op_combo.get()]
            self.setarEntradas()

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
            y = int(y_str, 2)
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

        self.audioFila.append("./audio/" + path)
        
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


def interfaceTerminal(alu):
    with open("texto/UFRJascii.txt", "r", encoding="utf-8") as f:
        banner = f.read()
        print(banner)
    """ Roda a ULA inteira no modo terminal """
    
    # Imprime o Banner
    print_banner_setup()

    while True:
        print_menu_modo()
        
        try:
            modo = inputLoop(f"{INDENT}Digite sua Opção: ", tipo=int, min_v=1, max_v=2)
        except (KeyboardInterrupt, EOFError):
            print(f"\n{INDENT}Saindo...")
            break

        if modo == 1: # MANUAL
            modo_manual(alu)
        elif modo == 2: # AUTOMATICO
            modo_automatico(alu)
        
        print("\n" + INDENT + "--- Operação Concluída ---")
        input(INDENT + "Pressione Enter para voltar ao menu principal...")
        print("\n" * 5) # Limpa a tela
        

if __name__ == "__main__":

    print("")
    
    #Cria os objetos centrais UMA VEZ 
    alu_principal = ALU_8bit()
    
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
        print(f"{INDENT}Iniciando Interface de Terminal...")
        interfaceTerminal(alu_principal)
