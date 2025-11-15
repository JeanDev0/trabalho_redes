import socket
import os
import sys

HOST_SERVIDOR = '127.0.0.1'
PORTA_SERVIDOR = 6000
PASTA_BACKUPS = "backups_recebidos"

def solicitar_backup(nome_arquivo):
    
    if not os.path.exists(PASTA_BACKUPS):
        os.makedirs(PASTA_BACKUPS)
        print(f"[INFO] Pasta '{PASTA_BACKUPS}' criada.")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST_SERVIDOR, PORTA_SERVIDOR))
        
        with sock:
            server_file = sock.makefile('rw', encoding='utf-8')
            
            print(f"[PEDIDO] Solicitando arquivo: {nome_arquivo}")
            server_file.write(f"GET|{nome_arquivo}\n")
            server_file.flush()
            
            resposta = server_file.readline().strip()
            
            if resposta.startswith("OK"):
                _, tamanho_str = resposta.split(' ', 1)
                tamanho = int(tamanho_str)
                print(f"[RESPOSTA] Servidor respondeu OK ({tamanho} bytes). Recebendo...")
                
                conteudo_bytes = sock.recv(tamanho)
                
                if len(conteudo_bytes) != tamanho:
                    print(f"[ERRO] Recebido {len(conteudo_bytes)} bytes, esperado {tamanho} bytes. Arquivo pode estar corrompido.")
                
                caminho_salvar = os.path.join(PASTA_BACKUPS, nome_arquivo)
                with open(caminho_salvar, 'wb') as f:
                    f.write(conteudo_bytes)
                    
                print(f"[SUCESSO] Arquivo salvo em: {caminho_salvar}")
                
            elif resposta.startswith("ERR"):
                _, msg_erro = resposta.split(' ', 1)
                print(f"[ERRO SERVIDOR] {msg_erro}")
            else:
                print(f"[ERRO] Resposta desconhecida do servidor: {resposta}")

    except Exception as e:
        print(f"[ERRO CONEXÃO] Nao foi possivel conectar ou baixar: {e}")

def main():
    print("--- Cliente de Backup (Questão 5) ---")
    if len(sys.argv) > 1:
        nome_arquivo = sys.argv[1]
    else:
        nome_arquivo = input("Digite o nome do arquivo para backup (ex: nginx.conf): ")
    
    if not nome_arquivo:
        print("Nome de arquivo invalido.")
        return
        
    solicitar_backup(nome_arquivo)

if __name__ == "__main__":
    main()