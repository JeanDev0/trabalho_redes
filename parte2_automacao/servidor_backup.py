import socket
import os

HOST = '0.0.0.0'
PORTA = 6000
PASTA_CONFIGS = "." 

print(f"[SERVIDOR BACKUP] Iniciado em {HOST}:{PORTA}")
print(f"Servindo arquivos da pasta: {os.path.abspath(PASTA_CONFIGS)}")

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PORTA))
servidor.listen(1)

while True:
    try:
        conn, addr = servidor.accept()
        print(f"\n[CONEXÃO] Cliente {addr} conectado.")
        
        with conn:
            client_file = conn.makefile('rw', encoding='utf-8')
            
            pedido = client_file.readline().strip()
            
            if not pedido.startswith("GET|"):
                print("[ERRO] Pedido mal formatado.")
                client_file.write("ERR Pedido mal formatado. Use: GET|nome_arquivo\n")
                continue
                
            _, nome_arquivo = pedido.split('|', 1)
            caminho_arquivo = os.path.join(PASTA_CONFIGS, nome_arquivo)
            
            print(f"[PEDIDO] Cliente solicitou: {nome_arquivo}")

            if os.path.isfile(caminho_arquivo):
                try:
                    with open(caminho_arquivo, 'rb') as f:
                        conteudo_bytes = f.read()
                        
                    tamanho = len(conteudo_bytes)
                    
                    client_file.write(f"OK {tamanho}\n")
                    client_file.flush()
                    
                    conn.sendall(conteudo_bytes)
                    
                    print(f"[ENVIO] Arquivo '{nome_arquivo}' ({tamanho} bytes) enviado.")
                    
                except Exception as e:
                    print(f"[ERRO] Falha ao ler arquivo: {e}")
                    client_file.write(f"ERR Falha ao ler arquivo no servidor: {e}\n")
            else:
                print(f"[ERRO] Arquivo '{nome_arquivo}' nao encontrado.")
                client_file.write(f"ERR Arquivo '{nome_arquivo}' nao encontrado.\n")

    except Exception as e:
        print(f"[ERRO SERVIDOR] Erro: {e}")
    except KeyboardInterrupt:
        print("\n[SERVIDOR BACKUP] Desligando...")
        break

servidor.close()