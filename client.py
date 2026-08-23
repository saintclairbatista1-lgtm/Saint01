import hmac
import hashlib
import time
import json
import sqlite3
import os
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- CONFIGURAÇÕES DO S MESSAGE (NÍVEL DEF + LEDGER LOCAL) ---
URL_API = "http://127.0.0.1:10000/api/v1/secure-transfer-def"
MASTER_SECRET = b"\xfa\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff" * 2 
DB_FILE = "s_message_ledger.db"

WALLET_FROM = "carteira_santi_123"
WALLET_TO = "carteira_destino_456"
ASSET_CODE = "BRL_DIGITAL"
AMOUNT = "50.0"
FOTO_PATH = "/storage/emulated/0/Pictures/Screenshots/foto1.png"

def inicializar_banco_local():
    """Garante a estrutura completa do banco local para ledger e filas offline."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Tabela de saldos locais (Ledger)
    c.execute('''
        CREATE TABLE IF NOT EXISTS wallet_balances (
            wallet_address TEXT,
            asset_code TEXT,
            balance REAL,
            PRIMARY KEY (wallet_address, asset_code)
        )
    ''')
    
    # Fila offline blindada (Nível DEF) para pacotes cifrados
    c.execute('''
        CREATE TABLE IF NOT EXISTS def_offline_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encrypted_payload BLOB,
            nonce BLOB,
            timestamp REAL
        )
    ''')
    
    conn.commit()
    conn.close()

def injetar_saldo_inicial(wallet: str, asset: str, valor: float):
    """Mantém a ferramenta de injeção e controle de saldo local."""
    inicializar_banco_local()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO wallet_balances (wallet_address, asset_code, balance)
        VALUES (?, ?, ?)
        ON CONFLICT(wallet_address, asset_code) 
        DO UPDATE SET balance = balance + ?
    ''', (wallet, asset, valor, valor))
    conn.commit()
    conn.close()
    print(f"[*] Ledger Local: Saldo de {valor} {asset} injetado/atualizado para {wallet}.")

def criptografar_payload(dados_dict: dict) -> tuple:
    """Aplica blindagem simétrica AES-256-GCM ao payload."""
    aesgcm = AESGCM(MASTER_SECRET)
    nonce = os.urandom(12)
    data_bytes = json.dumps(dados_dict).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, data_bytes, associated_data=None)
    return ciphertext, nonce

def gerar_assinatura_def(wallet_from: str, wallet_to: str, amount: str, timestamp: int) -> str:
    """Gera o HMAC-SHA256 vinculado ao timestamp (Anti-Replay)."""
    mensagem = f"{wallet_from}:{wallet_to}:{amount}:{timestamp}"
    return hmac.new(MASTER_SECRET[:16], mensagem.encode("utf-8"), hashlib.sha256).hexdigest()

def enfileirar_offline_def(ciphertext: bytes, nonce: bytes):
    """Guarda o pacote cifrado na fila offline se houver queda de rede."""
    inicializar_banco_local()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO def_offline_queue (encrypted_payload, nonce, timestamp) VALUES (?, ?, ?)",
        (ciphertext, nonce, time.time())
    )
    conn.commit()
    conn.close()
    print("[!] [DEF-SEC] Enlace indisponível. Pacote retido com segurança na fila offline local.")

def executar_cliente_completo():
    # Inicializa o ecossistema de banco de dados e ledger
    inicializar_banco_local()
    injetar_saldo_inicial(WALLET_FROM, ASSET_CODE, 150.0)
    
    timestamp_atual = int(time.time())
    
    print("[*] [DEF-SEC] Gerando assinatura HMAC e blindagem AES-256-GCM...")
    digital_signature = gerar_assinatura_def(WALLET_FROM, WALLET_TO, AMOUNT, timestamp_atual)
    
    payload_claro = {
        "asset_code": ASSET_CODE,
        "amount": AMOUNT,
        "wallet_from": WALLET_FROM,
        "wallet_to": WALLET_TO,
        "timestamp": timestamp_atual,
        "digital_signature": digital_signature
    }
    
    # Criptografa o pacote inteiro
    ciphertext, nonce = criptografar_payload(payload_claro)
    
    multipart_data = {
        "nonce": nonce.hex(),
        "enc_payload": ciphertext.hex()
    }
    
    try:
        print(f"[*] Lendo vetor biométrico (OpenCV) em: {FOTO_PATH}")
        with open(FOTO_PATH, "rb") as f:
            files = {"face_image": ("biometria.png", f, "image/png")}
            
            print("[+] Disparando requisição blindada para o S Message...")
            response = requests.post(URL_API, data=multipart_data, files=files, timeout=5)
            
        print(f"\n[HTTP Status] {response.status_code}")
        print(f"[Resposta] {response.json()}")
        
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # Falha de conexão: aciona a fila offline inteligente
        enfileirar_offline_def(ciphertext, nonce)
        
    except FileNotFoundError:
        print(f"[-] Erro: Arquivo de imagem biométrica não encontrado em {FOTO_PATH}.")
    except Exception as e:
        print(f"[-] Erro inesperado: {e}")

if __name__ == "__main__":
    executar_cliente_completo()
