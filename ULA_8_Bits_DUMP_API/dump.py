import subprocess
import time
import serial
import sys
import os

arduinoPort = "COM3"
arduinoSerial = None

try:
    avrdude_conf = os.path.expandvars(r"%USERPROFILE%\AppData\Local\Arduino15\packages\arduino\tools\avrdude\6.3.0-arduino17\etc\avrdude.conf")
    avrdude_exe = os.path.join(os.path.dirname(avrdude_conf), "..", "bin", "avrdude.exe")

    if not os.path.exists(avrdude_exe):
        print(f"Erro: Não foi possível encontrar 'avrdude.exe' no caminho:")
        print(avrdude_exe)
        sys.exit(1)

    if arduinoSerial == None:
       arduinoSerial = serial.Serial(arduinoPort, 115200, timeout=10)

except serial.SerialException as e:
    print(f"Erro: Não foi possível abrir a porta {arduinoPort}.")
    print(f"Detalhes: {e}")
    arduinoSerial = None


except Exception as e:
    print(f"Ocorreu um erro ao configurar os Caminhos: {e}")
    sys.exit(1)


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
  if (arduinoSerial == None):
      return

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

def get_serial_dump(arduinoSerial, comando, tamanho, file_name):
    if (arduinoSerial == None):
        return

    try:
        arduinoSerial.write(comando)
        data = arduinoSerial.read(tamanho)
        
        if len(data) != tamanho:
            print(f"ERRO: Esperava {tamanho} bytes, mas recebeu {len(data)}")
            return
        
        with open(file_name, "wb") as f:
            f.write(data)
        
    except Exception as e:
        print(f"Ocorreu um erro inesperado na comunicação serial: {e}")


def registradores_gerais_dump():
    get_serial_dump(arduinoSerial, b'G', 32, "geral_dump.bin")

def registradores_IO_dump():
    get_serial_dump(arduinoSerial, b'I', 224, "io_dump.bin")

def sram_dump():
    get_serial_dump(arduinoSerial, b'S', 2048, "sram_dump.bin")


def full_dump():
    eeprom_dump()
    flash_dump()

    try:
        registradores_gerais_dump()
        registradores_IO_dump()
        sram_dump()
            
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")



if __name__ == "__main__":
    full_dump()
