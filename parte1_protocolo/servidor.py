import socket
import threading
import time
import sys

HOST = '0.0.0.0'
PORTA = 5000
LOG_FILE = 'alertas.log'

clientes_conectados = {}
lock_clientes = threading.Lock()

def logar_alerta(partes_msg):
    comando, origem, destino, timestamp, corpo = partes_msg
    log_entry = f"[{timestamp}] {comando} de {origem} para {destino}: {corpo}\n"
    try:
        with open(LOG_FILE, "a", encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"[ERRO LOG] Falha ao escrever no log: {e}")

def enviar_para_todos(mensagem_bytes, origem_login):
    with lock_clientes:
        lista_sockets = clientes_conectados.items()
    for login, cliente_info in lista_sockets:
        if login != origem_login:
            try:
                cliente_info["socket"].send(mensagem_bytes)
            except Exception as e:
                print(f"[ERRO ENVIO] Falha ao enviar para {login}: {e}")

def enviar_para_um(mensagem_bytes, destino_login):
    socket_destino = None
    with lock_clientes:
        if destino_login in clientes_conectados:
            socket_destino = clientes_conectados[destino_login]["socket"]
    if socket_destino:
        try:
            socket_destino.send(mensagem_bytes)
            return True
        except Exception as e:
            print(f"[ERRO ENVIO] Falha ao enviar para {destino_login}: {e}")
            return False
    else:
        return False

def enviar_mensagem_servidor(destino_login, corpo_msg):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    mensagem = f"ACK|servidor|{destino_login}|{timestamp}|{corpo_msg}\n"
    enviar_para_um(mensagem.encode('utf-8'), destino_login)

def tratar_cliente(client_socket, address):
    login = None
    client_file = None 
    try:
        client_file = client_socket.makefile('r', encoding='utf-8')
        login_linha = client_file.readline()
        if not login_linha:
            raise ConnectionError("Desconexão antes do login (linha vazia)")
        login = login_linha.strip()

        with lock_clientes:
            if not login or login in clientes_conectados:
                client_socket.send(b"ERRO|servidor|login|...|Login invalido ou ja em uso.\n")
                raise ConnectionError("Login invalido ou duplicado")
            clientes_conectados[login] = {"socket": client_socket, "address": address}
            print(f"[LOGIN] Cliente '{login}' conectado de {address}.")
        
        enviar_mensagem_servidor(login, f"Bem-vindo {login}! Conectado ao NetOpsChat.")

        while True:
            mensagem_str = client_file.readline()
            if not mensagem_str:
                break

            mensagem_str = mensagem_str.strip()
            if not mensagem_str:
                continue

            try:
                partes = mensagem_str.split('|', 4)
                if len(partes) != 5:
                    enviar_mensagem_servidor(login, f"ERRO: Mensagem mal formatada. Esperava 5 partes.")
                    continue
                
                comando, origem, destino, timestamp, corpo = partes

                if origem != login:
                    enviar_mensagem_servidor(login, f"ERRO: Origem '{origem}' nao corresponde ao seu login '{login}'.")
                    continue
                
                mensagem_bytes_com_nl = f"{mensagem_str}\n".encode('utf-8')

                if comando == "MSG":
                    if destino == "ALL":
                        enviar_para_todos(mensagem_bytes_com_nl, login)
                    else:
                        if not enviar_para_um(mensagem_bytes_com_nl, destino):
                            enviar_mensagem_servidor(login, f"ERRO: Destino '{destino}' nao encontrado.")
                
                elif comando == "ALERT":
                    logar_alerta(partes)
                    if destino == "ALL":
                        enviar_para_todos(mensagem_bytes_com_nl, login)
                    else:
                        if not enviar_para_um(mensagem_bytes_com_nl, destino):
                            enviar_mensagem_servidor(login, f"ERRO: Destino '{destino}' nao encontrado para o alerta.")
                
                elif comando == "LIST":
                    with lock_clientes:
                        lista_logins = ", ".join(clientes_conectados.keys())
                    enviar_mensagem_servidor(login, f"Clientes conectados: {lista_logins}")
                
                elif comando == "EXIT":
                    print(f"[SAIDA] Cliente '{login}' solicitou desconexao.")
                    break 
                
                else:
                    enviar_mensagem_servidor(login, f"ERRO: Comando '{comando}' desconhecido.")
            
            except Exception as e:
                print(f"[ERRO PARSE] Erro ao processar msg de {login}: {e}")
                enviar_mensagem_servidor(login, "ERRO: Ocorreu um erro interno ao processar sua mensagem.")

    except (ConnectionResetError, ConnectionError, BrokenPipeError) as e:
        print(f"[DESCONEXAO] Cliente '{login}' (ou pre-login) desconectou: {e}")
    except Exception as e:
        print(f"[ERRO THREAD] Erro inesperado na thread de {login}: {e}")
    finally:
        if client_file:
            try:
                client_file.close()
            except:
                pass 

        if login and login in clientes_conectados:
            with lock_clientes:
                if login in clientes_conectados:
                    clientes_conectados[login]["socket"].close()
                    del clientes_conectados[login]
            print(f"[DESCONECTADO] Cliente '{login}' removido.")
        else:
            client_socket.close()
            print(f"[DESCONECTADO] Conexao anonima de {address} fechada.")

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        servidor.bind((HOST, PORTA))
        servidor.listen(10)
        print(f"[SERVIDOR] NetOpsChat iniciado em {HOST}:{PORTA}...")

        while True:
            try:
                client_socket, address = servidor.accept()
                thread = threading.Thread(target=tratar_cliente, args=(client_socket, address), daemon=True)
                thread.start()
            except Exception as e:
                print(f"[ERRO ACCEPT] Falha ao aceitar conexao: {e}")
    
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Desligando...")
    except Exception as e:
        print(f"[ERRO SERVIDOR] Erro fatal: {e}")
    finally:
        servidor.close()
        print("[SERVIDOR] Servidor fechado.")

if __name__ == "__main__":
    iniciar_servidor()
