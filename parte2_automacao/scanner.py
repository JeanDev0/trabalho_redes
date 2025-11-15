import socket
import threading
import sys
from queue import Queue

PORTA_ALVO = 80
TIMEOUT_SOCKET = 0.5
NUM_THREADS = 50

fila_ips = Queue()
hosts_ativos = []
lock_lista = threading.Lock()


def parse_ip_range(range_str):
    try:
        partes = range_str.split('-')
        ip_inicio_str = partes[0]
        
        ip_base = ".".join(ip_inicio_str.split('.')[:-1]) + "."
        num_inicio = int(ip_inicio_str.split('.')[-1])

        if len(partes) == 1:
            return [ip_inicio_str]
        
        num_fim = int(partes[1].split('.')[-1])

        lista_ips = []
        for i in range(num_inicio, num_fim + 1):
            lista_ips.append(f"{ip_base}{i}")
        
        return lista_ips
        
    except Exception as e:
        print(f"[ERRO] Formato de faixa de IP inválido: {e}")
        return None

def worker_scanner():
    while not fila_ips.empty():
        try:
            ip = fila_ips.get_nowait()
        except Queue.empty:
            break
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT_SOCKET)
            
            resultado = sock.connect_ex((ip, PORTA_ALVO))
            
            if resultado == 0 or resultado == 111:
                with lock_lista:
                    hosts_ativos.append(ip)
                    print(f"[ATIVO] Host encontrado: {ip}")
            else:
                print(f"[INATIVO] Host não responde: {ip}")
                
            sock.close()
            
        except socket.timeout:
            print(f"[INATIVO] Host não responde (timeout): {ip}")
        except Exception as e:
            print(f"[ERRO] Erro ao escanear {ip}: {e}")
        finally:
            fila_ips.task_done()

def main():
    print("--- Scanner de Hosts Ativos (Questão 1) ---")
    
    range_str = input("Digite a faixa de IPs (ex: 192.168.0.1-192.168.0.10): ")
    
    lista_ips = parse_ip_range(range_str)
    
    if not lista_ips:
        return

    print(f"\n[INFO] Escaneando {len(lista_ips)} IPs na porta {PORTA_ALVO} com {NUM_THREADS} threads...")
    
    for ip in lista_ips:
        fila_ips.put(ip)

    threads = []
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=worker_scanner, daemon=True)
        t.start()
        threads.append(t)
        
    fila_ips.join()

    print("\n--- Relatório Final ---")
    print(f"Total de hosts ativos: {len(hosts_ativos)}")
    
    hosts_ativos.sort()
    for ip in hosts_ativos:
        print(f"- {ip}")

    try:
        with open("hosts_ativos.txt", "w", encoding="utf-8") as f:
            f.write(f"Total de hosts ativos: {len(hosts_ativos)}\n")
            f.write("="*20 + "\n")
            for ip in hosts_ativos:
                f.write(f"{ip}\n")
        print(f"\n[INFO] Relatório salvo em 'hosts_ativos.txt'")
    except Exception as e:
        print(f"\n[ERRO] Falha ao salvar relatório: {e}")

if __name__ == "__main__":
    main()