# Instruções de Execução - Parte 1 (NetOpsChat)

## Pré-requisitos

* Python 3
* Bibliotecas: `customtkinter`, `ctkmessagebox`

Instale as bibliotecas com:
`pip install customtkinter ctkmessagebox`

## 1. Executando o Servidor

O servidor deve ser iniciado primeiro, pois ele aguarda as conexões dos clientes.

1.  Navegue até a pasta `parte1_protocolo/`.
2.  Execute o servidor:

    ```bash
    python servidor.py
    ```

3.  O terminal exibirá: `[SERVIDOR] NetOpsChat iniciado em 0.0.0.0:5000...`

## 2. Executando o Cliente

Você pode abrir vários clientes em terminais diferentes.

1.  Navegue até a pasta `parte1_protocolo/`.
2.  Execute o cliente:

    ```bash
    python cliente.py
    ```

3.  A interface gráfica será aberta.
4.  Digite um login único (ex: `tecnico01`) e clique em "Conectar".

## 3. Comandos do Cliente

* **Mensagem normal:** Apenas digite e envie. Será enviado para `ALL`.
* `/list`: Lista todos os usuários conectados.
* `/w <login> <mensagem>`: Envia uma mensagem privada (ex: `/w tecnico02 Olá`).
* `/exit`: Desconecta do chat.