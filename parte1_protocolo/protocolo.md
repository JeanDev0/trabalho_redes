# Especificação do Protocolo - NetOpsChat

Este documento descreve o protocolo de aplicação de texto sobre TCP usado para a comunicação entre o servidor e os clientes do NetOpsChat.

## 1. Formato Geral da Mensagem

Todas as mensagens são linhas de texto, terminadas com `\n` (quebra de linha). O formato geral usa o caractere `|` (pipe) como separador.

`COMANDO|ORIGEM|DESTINO|TIMESTAMP|CORPO`

## 2. Descrição dos Campos

* **COMANDO**: O tipo da mensagem.
    * `MSG`: Mensagem de chat normal.
    * `ALERT`: Alerta de rede (gerado por scripts ou técnicos).
    * `LIST`: Pedido para listar clientes conectados.
    * `EXIT`: Pedido de desconexão.
    * `ACK`: Confirmação de recebimento (usado pelo servidor para responder).
    * `ERRO`: Usado pelo servidor para reportar falhas (ex: login duplicado, msg mal formatada).

* **ORIGEM**: O login do cliente que envia a mensagem (ex: `tecnico01`, `script_ping`).

* **DESTINO**: O login do destinatário.
    * `ALL`: Enviar para todos os clientes (broadcast).
    * `servidor`: Mensagem destinada ao servidor (ex: `LIST`, `EXIT`).
    * `tecnico02`: Enviar apenas para um cliente específico.

* **TIMESTAMP**: Data e hora da mensagem (ex: `2025-11-07T10:32:15`).

* **CORPO**: O conteúdo da mensagem (texto livre).

## 3. Exemplos de Mensagens

* **Login (Cliente -> Servidor):**
    * O cliente envia apenas seu login com `\n` (ex: `tecnico01\n`).

* **Resposta de Login (Servidor -> Cliente):**
    * `ACK|servidor|tecnico01|2025-11-15T12:00:00|Bem-vindo tecnico01!`

* **Mensagem de Chat para Todos**:
    * `MSG|tecnico01|ALL|2025-11-15T12:01:00|Bom dia, equipe.`

* **Alerta de Rede**:
    * `ALERT|script_ping|noc|2025-11-15T12:02:00|Host 10.0.0.5 não respondeu.`

* **Pedido de Lista de Clientes**:
    * `LIST|tecnico01|servidor|2025-11-15T12:03:00|-`

* **Resposta da Lista de Clientes:**
    * `ACK|servidor|tecnico01|2025-11-15T12:03:01|Clientes conectados: tecnico01, script_ping`