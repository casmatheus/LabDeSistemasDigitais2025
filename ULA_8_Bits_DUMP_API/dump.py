import subprocess
import time
import serial
import serial.tools.list_ports
import sys
import os

ARQUIVO_REGISTRADORES_GERAIS_BINARIO = "geral_dump.bin"
ARQUIVO_REGISTRADORES_IO_BINARIO = "io_dump.bin"
ARQUIVO_EEPROM_BINARIO = "eeprom_dump.bin"
ARQUIVO_FLASH_BINARIO = "flash_dump.bin"
ARQUIVO_SRAM_BINARIO = "sram_dump.bin"

INDENT = "\t\t\t\t\t"
LINE_WIDTH = 80

IO_REGISTER_MAP = {
    # 0x20-0x2F
    0x03: "PINB", 0x04: "DDRB", 0x05: "PORTB", 0x06: "PINC", 0x07: "DDRC", 0x08: "PORTC", 0x09: "PIND", 0x0A: "DDRD", 0x0B: "PORTD",
    # 0x30-0x3F
    0x0F: "TIFR0", 0x10: "TIFR1", 0x11: "TIFR2", 0x15: "PCIFR", 0x16: "EIFR", 0x17: "EIMSK", 0x18: "GPIOR0", 0x19: "EECR", 0x1A: "EEDR", 0x1B: "EEARL", 0x1C: "EEARH", 0x1D: "GTCCR", 0x1E: "TCCR0A", 0x1F: "TCCR0B",
    # 0x40-0x4F
    0x20: "TCNT0", 0x21: "OCR0A", 0x22: "OCR0B", 0x24: "TCNT1L", 0x25: "TCNT1H", 0x26: "ICR1L", 0x27: "ICR1H", 0x28: "OCR1AL", 0x29: "OCR1AH", 0x2A: "OCR1BL", 0x2B: "OCR1BH", 0x2C: "GPIOR1", 0x2D: "GPIOR2",
    # 0x50-0x5F
    0x30: "SPCR", 0x31: "SPSR", 0x32: "SPDR", 0x34: "ACSR", 0x35: "SMCR", 0x36: "MCUSR", 0x37: "MCUCR", 0x3B: "SPMCSR", 0x3D: "SPL", 0x3E: "SPH", 0x3F: "SREG",
    # Extended I/O 0x60..0xFF
    0x40: "WDTCSR", 0x41: "CLKPR", 0x43: "PRR", 0x44: "OSCCAL", 0x46: "PCICR", 0x47: "EICRA", 0x49: "PCMSK0", 0x4A: "PCMSK1", 0x4B: "PCMSK2", 0x4C: "TIMSK0", 0x4D: "TIMSK1", 0x4E: "TIMSK2",
    # 0x70..
    0x58: "ADCL", 0x59: "ADCH", 0x5A: "ADCSRA", 0x5B: "ADCSRB", 0x5C: "ADMUX", 0x5E: "DIDR0", 0x5F: "DIDR1",
    # 0x80..
    0x60: "TCCR1A", 0x61: "TCCR1B", 0x62: "TCCR1C", 0x64: "TCNT2", 0x65: "OCR2A", 0x66: "OCR2B",
    # 0x90.. (nenhum)
    # 0xA0..
    0x80: "TWBR", 0x81: "TWSR", 0x82: "TWAR", 0x83: "TWDR", 0x84: "TWCR", 0x85: "TWAMR",
    # 0xB0..
    0x90: "UCSR0A", 0x91: "UCSR0B", 0x92: "UCSR0C", 0x94: "UBRR0L", 0x95: "UBRR0H", 0x96: "UDR0",
}

try:
    avrdude_conf = os.path.expandvars(r"%USERPROFILE%\AppData\Local\Arduino15\packages\arduino\tools\avrdude\6.3.0-arduino17\etc\avrdude.conf")
    avrdude_exe = os.path.join(os.path.dirname(avrdude_conf), "..", "bin", "avrdude.exe")

    if not os.path.exists(avrdude_exe):
        print(f"Erro: Não foi possível encontrar 'avrdude.exe' no caminho:")
        print(avrdude_exe)
        sys.exit(1)


except Exception as e:
    print(f"Ocorreu um erro ao configurar os Caminhos: {e}")
    sys.exit(1)


arduinoPort = None
avrdude_command = None

def find_arduino_port():
    """Encontra o port da Arduino"""
    global arduinoPort
    global avrdude_command
    
    portDevice = None
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        if "arduino" in port.description.lower():
            portDevice = port.device
    
    if portDevice is not None:
        arduinoPort = portDevice
        avrdude_command = [
            avrdude_exe,
            f"-C{avrdude_conf}",
            "-patmega328p",
            "-carduino",
            f"-P{arduinoPort}",
            "-b115200",
            "-U"
            ]

        return True
    else:
        arduinoPort = None
        avrdude_command = None
        return False

find_arduino_port()

def run_avrdude(tipo):
    find_arduino_port()
    if arduinoPort == None:
        return False
    
    comando = "" 
    if tipo == "eeprom":
        comando = avrdude_command + [f"eeprom:r:{ARQUIVO_EEPROM_BINARIO}:r"]
    elif tipo == "flash":
        comando = avrdude_command + [f"flash:r:{ARQUIVO_FLASH_BINARIO}:r"]
    else:
        return False

    try:
        result = subprocess.run(comando, check=True, text=True, capture_output=True)
      
    except subprocess.CalledProcessError as e:
        print(f"O avrdude falhou com o código de retorno: {e.returncode}")
        print("\n--- Informações do avrdude (stderr) ---")
        print(e.stderr)
        print("\n--- Saída do avrdude (stdout) ---")
        print(e.stdout)

        find_arduino_port()
        return False
  
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

        find_arduino_port()
        return False

    return True


def eeprom_dump():
    return run_avrdude("eeprom")

def flash_dump():
    return run_avrdude("flash")

def get_serial_dump(comando, tamanho, file_name):
    find_arduino_port()
    if arduinoPort == None:
        return False

    try:
        arduinoSerial = serial.Serial(arduinoPort, 115200, timeout=10)
        time.sleep(2)

        arduinoSerial.write(comando)
        data = arduinoSerial.read(tamanho)
        
        if len(data) != tamanho:
            print(f"ERRO: Esperava {tamanho} bytes, mas recebeu {len(data)}")
            return
        
        with open(file_name, "wb") as f:
            f.write(data)

        return True
        
    except Exception as e:
        print(f"Ocorreu um erro inesperado na comunicação serial: {e}")
        find_arduino_port()

        return False


def registradores_gerais_dump():
    return get_serial_dump(b'G', 32, ARQUIVO_REGISTRADORES_GERAIS_BINARIO)

def registradores_IO_dump():
    return get_serial_dump(b'I', 224, ARQUIVO_REGISTRADORES_IO_BINARIO)

def sram_dump():
    return get_serial_dump(b'S', 2048, ARQUIVO_SRAM_BINARIO)


def full_dump():
    eeprom_dump()
    flash_dump()

    try:
        registradores_gerais_dump()
        registradores_IO_dump()
        sram_dump()
            
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

def dump_binary_file(filepath, title, indent = INDENT):
    BYTES_PER_LINE = 16
    LINE_WIDTH = 67

    output = []

    title_str = f" {title} "
    output.append(indent + title_str.center(LINE_WIDTH, '='))

    try:
        with open(filepath, 'rb') as f:
            offset = 0
            while True:
                # Read a chunk of 16 bytes
                chunk = f.read(BYTES_PER_LINE)
                if not chunk:
                    break  # End of file

                chunk_len = len(chunk)

                offset_str = indent + f"{offset:08x}: "  # e.g., "00000000: "

                hex_str_parts = []
                for i in range(8):
                    idx = i * 2
                    if idx + 1 < chunk_len:
                        hex_str_parts.append(f"{chunk[idx]:02x}{chunk[idx+1]:02x}")
                    elif idx < chunk_len:
                        hex_str_parts.append(f"{chunk[idx]:02x}  ")
                    else:
                        hex_str_parts.append("    ")
                
                hex_str = " ".join(hex_str_parts)

                ascii_str = ""
                for byte in chunk:
                    if 32 <= byte <= 126:
                        ascii_str += chr(byte)
                    else:
                        ascii_str += "."
                
                ascii_str_padded = f"{ascii_str:<16}"

                output.append(f"{offset_str}{hex_str}  {ascii_str_padded}")

                offset += chunk_len

    except FileNotFoundError:
        print(f"{indent}Erro: Arquivo não encontrado:'{filepath}'")
    except Exception as e:
        print(f"{indent}Um erro inesperado ocorreu: {e}")

    return "\n".join(output)

def dump_registradores_gerais(filepath, title, indent = INDENT):
    """ Função para exibir GPRs (R0-R31) com nomes."""
    
    GPR_NAMES = [f"R{i}" for i in range(32)]
    BYTES_PER_LINE = 8
    
    output = []

    title_str = f" {title} "
    output.append(indent + title_str.center(LINE_WIDTH, '='))

    try:
        with open(filepath, 'rb') as f:
            data = f.read() # Read all 32 bytes
        
        if len(data) != 32:
            print(f"{indent}Erro: O arquivo de GPRs não contém 32 bytes. Encontrado: {len(data)}")
            return

        for line_start_index in range(0, 32, BYTES_PER_LINE):
            line_parts = []
            # Get registers for this line
            for i in range(line_start_index, line_start_index + BYTES_PER_LINE):
                if i < 32:
                    reg_name = GPR_NAMES[i]
                    reg_value = data[i]
                    # Formata cada registrador: "Rxx: 00"
                    line_parts.append(f"{reg_name:>3}: {reg_value:02X}")
            
            # Imprime a linha
            output.append(indent + " | ".join(line_parts))

    except FileNotFoundError:
        print(f"{indent}Erro: Arquivo não encontrado:'{filepath}'")
    except Exception as e:
        print(f"{indent}Um erro inesperado ocorreu: {e}")

    return "\n".join(output)

def dump_registradores_io(filepath, title, register_map, indent = INDENT):
    """ Função para exibir Registradores I/O nomeados."""
    
    title_str = f" {title} "
    output = []
    output.append(indent + title_str.center(LINE_WIDTH, '='))

    try:
        with open(filepath, 'rb') as f:
            data = f.read() # Read all 224 bytes
        
        if len(data) != 224:
            print(f"{indent}Erro: O arquivo de I/O não contém 224 bytes. Encontrado: {len(data)}")
            return

        # Obter uma lista ordenada de offsets (chaves do mapa)
        sorted_offsets = sorted(register_map.keys())

        # Agrupar em linhas para melhor visualização (ex: 4 por linha)
        REGISTERS_PER_LINE = 4
        
        for i in range(0, len(sorted_offsets), REGISTERS_PER_LINE):
            line_parts = []
            # Obter os registradores para esta linha
            for j in range(i, i + REGISTERS_PER_LINE):
                if j < len(sorted_offsets):
                    offset = sorted_offsets[j]
                    mem_addr = offset + 0x20 # Endereço real na memória
                    reg_name = register_map[offset]
                    reg_value = data[offset]
                    # Formata: "REGNAME (0xMM): 00"
                    line_parts.append(f"{reg_name:>7} (0x{mem_addr:02X}): {reg_value:02X}")
            
            # Alinhar as colunas. Cada parte tem ~20 chars.
            formatted_parts = [f"{part:<20}" for part in line_parts]
            output.append(indent + "".join(formatted_parts))

    except FileNotFoundError:
        print(f"{indent}Erro: Arquivo não encontrado:'{filepath}'")
    except Exception as e:
        print(f"{indent}Um erro inesperado ocorreu: {e}")

    return "\n".join(output)

# --- FUNÇÕES DE HEATMAP (SVG) ---

def _gerar_svg_base(dados, titulos_linhas, titulo_geral):
    """
    Função interna genérica para criar o SVG.
    dados: lista/bytearray de valores inteiros.
    titulos_linhas: lista de strings para as legendas de cada linha.
    """
    num_linhas = len(dados)
    cell_w, cell_h = 25, 20
    margin_left = 80
    margin_top = 40
    width = margin_left + 8 * cell_w + 20
    height = margin_top + num_linhas * cell_h + 20

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet" class="heatmap-svg">']
    
    svg.append('<style>.heatmap-svg { font-family: monospace; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; }</style>')

    # Título Geral
    svg.append(f'<text x="{width/2}" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#343a40">{titulo_geral}</text>')

    # Cabeçalho dos Bits (7 a 0)
    for col in range(8):
        bit_num = 7 - col
        x = margin_left + col * cell_w + cell_w / 2
        svg.append(f'<text x="{x}" y="{margin_top - 8}" text-anchor="middle" font-size="10" fill="#6c757d">{bit_num}</text>')

    # Linhas
    for i in range(num_linhas):
        val = dados[i]
        y = margin_top + i * cell_h
        
        label = titulos_linhas[i] if i < len(titulos_linhas) else f"R{i}"
        svg.append(f'<text x="{margin_left - 8}" y="{y + cell_h/2 + 4}" text-anchor="end" font-size="11" fill="#495057">{label}</text>')

        for col in range(8):
            bit_val = (val >> (7 - col)) & 1
            fill = "#0d6efd" if bit_val else "#e9ecef"
            x = margin_left + col * cell_w
            svg.append(f'<rect x="{x}" y="{y}" width="{cell_w-1}" height="{cell_h-1}" fill="{fill}" rx="2"><title>Bit {7-col}: {bit_val}</title></rect>')

    svg.append('</svg>')
    return "".join(svg)


def heatmap_gerais_svg(filepath):
    """ Gera SVG para os 32 registradores gerais. """
    try:
        with open(filepath, 'rb') as f: data = f.read()
        if len(data) != 32: return None
    except: return None
    
    labels = [f"R{i:02d}" for i in range(32)]
    return _gerar_svg_base(data, labels, "Registradores Gerais")

def heatmap_io_svg(filepath, register_map):
    """ Gera SVG apenas para os registradores de I/O mapeados (com nome). """
    try:
        with open(filepath, 'rb') as f: full_data = f.read()
        if len(full_data) != 224: return None
    except: return None

    offsets_ordenados = sorted(register_map.keys())
    dados_filtrados = []
    labels = []
    
    for off in offsets_ordenados:
        dados_filtrados.append(full_data[off])
        labels.append(f"{register_map[off]} (0x{off+0x20:02X})")

    return _gerar_svg_base(dados_filtrados, labels, "Registradores de I/O")


if __name__ == "__main__":
    full_dump()
 
    print(dump_registradores_gerais(ARQUIVO_REGISTRADORES_GERAIS_BINARIO, "Registradores Gerais (R0-R31)"))
    print("\n")
    
    print(dump_registradores_io(ARQUIVO_REGISTRADORES_IO_BINARIO, "Registradores I/O (ATmega328p)", IO_REGISTER_MAP))
    print("\n")

    # Usando a função original para os outros arquivos
    print(dump_binary_file(ARQUIVO_SRAM_BINARIO, "SRAM Dump (2KB)"))
    print("\n")
    
    print(dump_binary_file(ARQUIVO_EEPROM_BINARIO, "EEPROM Dump (1KB)"))
    print("\n")

