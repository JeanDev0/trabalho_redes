import socket
import time

HOST_ALVO = '127.0.0.1'
TIMEOUT_SOCKET = 1.0

PORTAS_PARA_CHECAR = [
    22,    # SSH
    80,    # HTTP
    443,   # HTTPS
    5432,  # PostgreSQL (Exemplo do PDF)
    5000   # Nosso Servidor NetOpsChat
]

def check_local_port(porta):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT_SOCKET)
        
        resultado = sock.connect_ex((HOST_ALVO, porta))
        sock.close()
        
        return resultado == 0
        
    except Exception:
        return False

def main():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    
    print(f"--- Relatório de Verificação - {HOST_ALVO} ({timestamp}) ---")
    print("-" * (50 + len(HOST_ALVO) + len(timestamp)))

    falhas_criticas = 0

    for porta in PORTAS_PARA_CHECAR:
        if check_local_port(porta):
            print(f"Porta {porta:<5}: OK")
        else:
            print(f"Porta {porta:<5}: FALHA")
            falhas_criticas += 1
            
    print("-" * (50 + len(HOST_ALVO) + len(timestamp)))
    if falhas_criticas > 0:
        print(f"Resumo: {falhas_criticas} porta(s) críticas estão fechadas.")
    else:
        print("Resumo: Todos os serviços essenciais estão respondendo.")

if __name__ == "__main__":
    main()