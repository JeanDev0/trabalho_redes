import customtkinter
from CTkMessagebox import CTkMessagebox
import socket
import threading
import time
import sys

HOST_SERVIDOR = "127.0.0.1"
PORTA_SERVIDOR = 5000

cliente_socket = None
login = None
janela_conectada = False

def formatar_para_exibicao(mensagem_protocolo):
    try:
        partes = mensagem_protocolo.split('|', 4)
        if len(partes) < 5:
            return f"[SISTEMA] {mensagem_protocolo}\n"
        
        comando, origem, destino, timestamp, corpo = partes
        
        hora_formatada = timestamp.split('T')[-1] if 'T' in timestamp else timestamp
        
        return f"[{hora_formatada}] ({origem} -> {destino}) {comando}: {corpo}\n"
    except Exception as e:
        return f"[ERRO PARSE] {mensagem_protocolo} ({e})\n"

def exibir_mensagem_no_chat(mensagem):
    memo_mensagens.configure(state="normal")
    memo_mensagens.insert("end", mensagem)
    memo_mensagens.see("end")
    memo_mensagens.configure(state="disabled")

def receber_mensagem():
    global cliente_socket
    global janela_conectada

    while janela_conectada:
        try:
            dados_bytes = cliente_socket.recv(4096)
            if not dados_bytes:
                if janela_conectada:
                    exibir_mensagem_no_chat("[SISTEMA] O servidor encerrou a conexão.\n")
                break

            mensagens = dados_bytes.decode('utf-8').strip().split('\n')
            
            for msg_protocolo in mensagens:
                if msg_protocolo:
                    msg_formatada = formatar_para_exibicao(msg_protocolo)
                    exibir_mensagem_no_chat(msg_formatada)

        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            if janela_conectada:
                exibir_mensagem_no_chat("[SISTEMA] Conexão perdida com o servidor.\n")
                print(f"[ERRO RECV] Conexão perdida: {e}")
            break
        except Exception as e:
            if janela_conectada:
                print(f"[ERRO RECV] Erro inesperado: {e}")
            break
    
    print("Thread de recebimento encerrada.")
    campo_mensagem.configure(state="disabled")
    botao_enviar.configure(state="disabled")

def enviar_mensagem_protocolo(comando, destino, corpo):
    global cliente_socket
    global login
    
    if not login or not cliente_socket:
        CTkMessagebox(title="Erro", message="Você não está conectado.", icon="warning")
        return

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    mensagem = f"{comando}|{login}|{destino}|{timestamp}|{corpo}\n"
    
    try:
        cliente_socket.send(mensagem.encode('utf-8'))
        
        if comando == "MSG":
            msg_local = formatar_para_exibicao(mensagem.strip())
            exibir_mensagem_no_chat(msg_local)

    except Exception as e:
        CTkMessagebox(title="Erro", message=f"Erro no envio: {e}", icon="warning")

def on_enviar_click(event=None):
    corpo = campo_mensagem.get().strip()
    if not corpo:
        return
    
    comando = "MSG"
    destino = "ALL"
    
    if corpo.startswith("/list"):
        comando = "LIST"
        destino = "servidor"
        corpo = "-"
    elif corpo.startswith("/exit"):
        comando = "EXIT"
        destino = "servidor"
        corpo = "-"
    elif corpo.startswith("/w "):
        try:
            _, dest_login, msg_privada = corpo.split(" ", 2)
            destino = dest_login
            corpo = msg_privada
        except Exception:
            exibir_mensagem_no_chat("[SISTEMA] Formato de /w inválido. Use: /w <login> <mensagem>\n")
            campo_mensagem.delete(0, "end")
            return
            
    enviar_mensagem_protocolo(comando, destino, corpo)
    
    campo_mensagem.delete(0, "end")
    
    if comando == "EXIT":
        on_closing()

def conectar():
    global login
    global cliente_socket
    global janela_conectada

    nome_valor = campo_nome.get().strip()
    if not nome_valor:
        CTkMessagebox(title="Erro", message="Antes, digite seu login (ex: tecnico01)", icon="warning")
        return    
    
    login = nome_valor

    try:
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((HOST_SERVIDOR, PORTA_SERVIDOR))
        
       
        cliente_socket.send(f"{login}\n".encode('utf-8'))
   
        
        campo_mensagem.configure(state="normal")
        botao_enviar.configure(state="normal")
        botao_conectar.configure(state="disabled")
        campo_nome.configure(state="disabled")

        janela_conectada = True
        thread = threading.Thread(target=receber_mensagem, daemon=True)
        thread.start()
        
        exibir_mensagem_no_chat(f"[SISTEMA] Conectado ao servidor como '{login}'.\n")
        
        enviar_mensagem_protocolo("LIST", "servidor", "-")

    except Exception as e:
        CTkMessagebox(title="Erro", message=f"Erro na conexão: {e}", icon="warning")
        cliente_socket = None
        login = None

def on_closing():
    global janela_conectada
    global cliente_socket
    
    janela_conectada = False
    
    if cliente_socket:
        try:
            print("Enviando EXIT...")
            enviar_mensagem_protocolo("EXIT", "servidor", "Saindo")
            time.sleep(0.1)
            cliente_socket.close()
        except Exception as e:
            print(f"Erro ao enviar EXIT: {e}")
            
    janela.destroy()
    sys.exit()

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

janela = customtkinter.CTk()
janela.geometry("800x600")
janela.title(f"NetOpsChat Client (Conectar em {HOST_SERVIDOR}:{PORTA_SERVIDOR})")

label_nome = customtkinter.CTkLabel(janela, text="Digite seu Login (ex: tecnico01, script_ping)")
label_nome.pack(pady=(10,5))

campo_nome = customtkinter.CTkEntry(janela, width=250)
campo_nome.pack(pady=5)

botao_conectar = customtkinter.CTkButton(janela, text="Conectar", 
                                         command=conectar)
botao_conectar.pack(pady=(0,10))

memo_mensagens = customtkinter.CTkTextbox(janela, width=760, 
                                          height=300, state="disabled", font=("Consolas", 12))
memo_mensagens.pack(padx=10, pady=10, fill="both", expand=True)

frame = customtkinter.CTkFrame(janela)
frame.pack(fill="x", padx=10, pady=(0,10))

campo_mensagem = customtkinter.CTkEntry(frame, state="disabled")
campo_mensagem.pack(side="left", fill="x", expand=True, padx=(0,10))
campo_mensagem.bind("<Return>", on_enviar_click)

botao_enviar = customtkinter.CTkButton(frame, text="Enviar", 
                                       command=on_enviar_click, state="disabled")
botao_enviar.pack(side="right")

janela.protocol("WM_DELETE_WINDOW", on_closing)

janela.mainloop()
