import subprocess
import time
import serial
import sys
import os


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


arduinoPort = "COM3"
avrdude_command = [
    avrdude_exe,
    f"-C{avrdude_conf}",
    "-patmega328p",
    "-carduino",
    f"-P{arduinoPort}",
    "-b115200",
    "-U"
    ]

eeprom_dump_command = avrdude_command + ["eeprom:r:eeprom_dump.bin:r"]
flash_dump_command = avrdude_command + ["flash:r:flash_dump.bin:r"]

def run_avrdude(command):
  try:
      result = subprocess.run(command, check=True, text=True, capture_output=True)
      
  except subprocess.CalledProcessError as e:
      print(f"O avrdude falhou com o código de retorno: {e.returncode}")
      print("\n--- Informações do avrdude (stderr) ---")
      print(e.stderr)
      print("\n--- Saída do avrdude (stdout) ---")
      print(e.stdout)
  
  except Exception as e:
      print(f"Ocorreu um erro inesperado: {e}")


def eeprom_dump():
    run_avrdude(eeprom_dump_command)

def flash_dump():
    run_avrdude(flash_dump_command)

def get_serial_dump(ser, comando, tamanho, file_name):
    try:
        ser.write(comando)
        data = ser.read(tamanho)
        
        if len(data) != tamanho:
            print(f"ERRO: Esperava {tamanho} bytes, mas recebeu {len(data)}")
            return
        
        with open(file_name, "wb") as f:
            f.write(data)
        
    except Exception as e:
        print(f"Ocorreu um erro inesperado na comunicação serial: {e}")


def registradores_gerais_dump(ser):
    get_serial_dump(ser, b'G', 32, "geral_dump.bin")

def registradores_IO_dump(ser):
    get_serial_dump(ser, b'I', 224, "io_dump.bin")

def sram_dump(ser):
    get_serial_dump(ser, b'S', 2048, "sram_dump.bin")


def full_dump():
    eeprom_dump()
    flash_dump()

    try:
        ser = serial.Serial(arduinoPort, 115200, timeout=10)
        time.sleep(2)

        registradores_gerais_dump(ser)
        registradores_IO_dump(ser)
        sram_dump(ser)
            
    
    except serial.SerialException as e:
        print(f"--- [ERRO] ---")
        print(f"Não foi possível abrir a porta {arduinoPort}.")
        print("O Monitor Serial da IDE do Arduino está fechado?")
        print(f"Detalhes: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")



if __name__ == "__main__":
    full_dump()
