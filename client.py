import hmac
import hashlib
import time
import json
import sqlite3
import requests

# Configurações da transação
URL_API = "http://127.0.0.1:10000/api/v1/secure-transfer-biometric"
SECRET_KEY = b"sua_chave_secreta_compartilhada"  # Deve bater com a chave do servidor
DB_FILE = "s_message_ledger.db"

WALLET_FROM = "carteira_santi_123"
WALLET_TO = "carteira_destino_456"
ASSET_CODE = "BRL_DIGITAL"
AMOUNT = "50.0"
FOTO_PATH = "/storage/emulated/0/Pictures/Screenshots/foto1.png"

def inicializar_fila_offline():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS offline_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT,
            payload TEXT,
            timestamp REAL
        )
    ''')
    conn.commit()
    conn.close()

def salvar_offline(payload: dict):
    inicializar_fila_offline()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO offline_queue (endpoint, payload, timestamp) VALUES (?, ?, ?)",
        (URL_API, json.dumps(payload), time.time())
    )
    conn.commit()
    conn.close()
    print("[*] Sem conexão com o servidor. Transação salva na fila offline com sucesso.")

def gerar_assinatura_hmac(wallet_from: str, wallet_to: str, amount: str) -> str:
    mensagem = f"{wallet_from}:{wallet_to}:{amount}"
    return hmac.new(SECRET_KEY, mensagem.encode("utf-8"), hashlib.sha256).hexdigest()

def executar_cliente():
    print("[*] Gerando assinatura HMAC...")
    digital_signature = gerar_assinatura_hmac(WALLET_FROM, WALLET_TO, AMOUNT)
    
    payload = {
        "asset_code": ASSET_CODE,
        "amount": AMOUNT,
        "wallet_from": WALLET_FROM,
        "wallet_to": WALLET_TO,
        "digital_signature": digital_signature
    }
    
    try:
        print(f"[*] Lendo imagem biométrica em: {FOTO_PATH}")
        with open(FOTO_PATH, "rb") as f:
            files = {"face_image": ("foto1.png", f, "image/png")}
            
            print("[+] Disparando requisição para o S Message...")
            # Definimos um timeout curto para detectar queda rápido
            response = requests.post(URL_API, data=payload, files=files, timeout=5)
            
        print(f"\n[HTTP Status] {response.status_code}")
        print(f"[Resposta] {response.json()}")
        
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # Cai aqui se o servidor estiver offline
        salvar_offline(payload)
        
    except FileNotFoundError:
        print(f"[-] Erro: Arquivo de imagem não encontrado no caminho {FOTO_PATH}.")
    except Exception as e:
        print(f"[-] Erro inesperado: {e}")

if __name__ == "__main__":
    executar_cliente()
