import sys
import subprocess
import re
import platform
import statistics

def monitorar_latencia(host, tentativas=5):
    os_name = platform.system().lower()
    
    if os_name == "windows":
        comando = ["ping", "-n", str(tentativas), host]
        regex_latencia = r"tempo[=<]([\d\.]+)ms|time[=<]([\d\.]+)ms"
        regex_perda = r"(\d+)%\s*(?:de\s+perda|loss)"
        encoding = 'cp1252'
    else:
        comando = ["ping", "-c", str(tentativas), host]
        regex_latencia = r"time=([\d\.]+) ms"
        regex_perda = r"(\d+)% packet loss"
        encoding = 'utf-8'

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=15,
            encoding=encoding,
            errors='ignore'
        )
        output = resultado.stdout
        if resultado.returncode != 0 and not output:
            print(f"[ERRO] Falha ao executar ping. Host '{host}' está inacessível.")
            return
    except subprocess.TimeoutExpired:
        print("[ERRO] Teste de ping excedeu o tempo limite (15s).")
        return
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro inesperado: {e}")
        return

    latencias_ms = []
    matches_latencia = re.findall(regex_latencia, output)

    for m in matches_latencia:
        valor = next((v for v in m if v), None)
        if valor:
            latencias_ms.append(float(valor))

    match_perda = re.search(regex_perda, output)
    perda_pct = float(match_perda.group(1)) if match_perda else 0.0

    if latencias_ms:
        avg_lat = statistics.mean(latencias_ms)
        max_lat = max(latencias_ms)
    else:
        avg_lat = 0.0
        max_lat = 0.0

    print("\n--- Resumo da Conectividade ---")
    print(f"Host: {host}")
    print(f"Tentativas: {tentativas} (Recebidas: {len(latencias_ms)})")
    print(f"Latência média: {avg_lat:.2f} ms")
    print(f"Latência máxima: {max_lat:.2f} ms")
    print(f"Perda: {perda_pct:.0f}% ({int(tentativas * (perda_pct / 100.0))} de {tentativas})")


def main():
    print("--- Medidor de Latência e Perda (Questão 3) ---")
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = input("Digite o host para testar (ex: google.com ou 8.8.8.8): ")

    if not host:
        print("Nenhum host fornecido. Saindo.")
        return

    monitorar_latencia(host, tentativas=5)


if __name__ == "__main__":
    main()
