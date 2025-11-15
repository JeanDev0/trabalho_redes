import socket
import sys

CONFIG_FILE = "servicos.txt"
TIMEOUT_SOCKET = 2.0 

def check_port(ip, porta):
    try:
        porta_int = int(porta)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT_SOCKET)
        
        resultado = sock.connect_ex((ip, porta_int))
        
        sock.close()
        
        return resultado == 0
        
    except socket.timeout:
        return False
    except socket.error:
        return False
    except ValueError:
        return False
    except Exception:
        return False

def main():
    print(f"--- Monitor de Portas de Serviço (Questão 2) ---") 
    print(f"Lendo do arquivo: {CONFIG_FILE}\n") 
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de configuração '{CONFIG_FILE}' não encontrado.")
        print("Por favor, crie o arquivo com o formato: nome;ip;porta") 
        return
    except Exception as e:
        print(f"[ERRO] Falha ao ler o arquivo: {e}")
        return

    if not linhas:
        print("[AVISO] Arquivo de configuração está vazio.")
        return

    for linha in linhas:
        linha = linha.strip()
        
        if not linha or linha.startswith("#"):
            continue
        
        partes = linha.split(';')
        
        if len(partes) != 3:
            print(f"[AVISO] Linha mal formatada, pulando: '{linha}'")
            continue
            
        nome_servico = partes[0]
        ip = partes[1]
        porta = partes[2]
        
        if check_port(ip, porta):
            print(f"[OK]    {nome_servico} ({ip}:{porta})") 
        else:
            print(f"[FALHA] {nome_servico} ({ip}:{porta})") 

if __name__ == "__main__":
    main()