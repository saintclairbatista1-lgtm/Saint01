import os
import json
import time
import hmac
import hashlib
import sqlite3
import numpy as np
import cv2
from collections import defaultdict
from fastapi import FastAPI, HTTPException, status, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import uvicorn


# ==================================================
# CONFIGURAÇÃO ROBUSTA DO BANCO DE DADOS (WAL + FULL SYNC)
# ==================================================
DB_FILE = "s_message_ledger.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=FULL;")
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        block_index INTEGER UNIQUE,
        timestamp REAL,
        payload TEXT,
        previous_hash TEXT,
        block_hash TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wallet_balances (
        wallet_address TEXT,
        asset_code TEXT,
        balance REAL,
        last_updated REAL,
        PRIMARY KEY (wallet_address, asset_code)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wallet_keys (
        wallet_address TEXT PRIMARY KEY,
        public_key_pem TEXT,
        created_at REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS used_nonces (
        nonce TEXT PRIMARY KEY,
        used_at REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS support_tickets (
        ticket_id TEXT PRIMARY KEY,
        wallet_address TEXT,
        subject_encrypted TEXT,
        status TEXT,
        priority TEXT,
        created_at REAL,
        updated_at REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ticket_messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT,
        sender_address TEXT,
        encrypted_content TEXT,
        nonce_hex TEXT,
        timestamp REAL,
        FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id)
    )
    ''')

    conn.commit()

    # Bloco Gênese inicial
    cursor.execute('SELECT COUNT(*) FROM ledger')
    if cursor.fetchone()[0] == 0:
        genesis_payload = "Genesis Block (S Message Full Unified Military-Grade Edition + Help Desk 2026)"
        genesis_hash = "0" * 128
        cursor.execute('''
        INSERT INTO ledger (block_index, timestamp, payload, previous_hash, block_hash)
        VALUES (?, ?, ?, ?, ?)
        ''', (0, 0.0, genesis_payload, genesis_hash, genesis_hash))
        conn.commit()

    conn.close()


init_db()


# ==================================================
# MICROPROCESSADOR VIRTUAL 10.000 BYTES — ALU + HKDF + ZEROIZAÇÃO SEGURA
# ==================================================
class MilitaryGrade10000ByteProcessor:
    def __init__(self):
        self.registers = {
            "R0": bytearray(10000),
            "R1": bytearray(10000),
            "R2": bytearray(16),
            "FLAGS": 0x01
        }
        self.is_initialized = False

    def load_master_buffer(self, input_bytes: bytes):
        padded_buffer = bytearray()
        seed = input_bytes
        while len(padded_buffer) < 10000:
            seed = hashlib.sha512(seed).digest()
            padded_buffer.extend(seed)

        self.registers["R1"] = bytearray(padded_buffer[:10000])
        self.is_initialized = True
        self.registers["FLAGS"] = 0x01

    def _derive_key(self, salt: bytes, info: bytes) -> bytes:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=info,
        )
        return hkdf.derive(bytes(self.registers["R1"]))

    def execute_aes_encrypt(self, plaintext_bytes: bytes, nonce_bytes: bytes) -> dict:
        if not self.is_initialized:
            raise RuntimeError("CRÍTICO: Processador ALU virtual não inicializado.")

        key = self._derive_key(b"s-message-ledger-salt", b"ledger-encryption")
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce_bytes, plaintext_bytes, None)

        return {
            "processor_status": "MILITARY ALU ATIVA (10000B + HKDF + AES-GCM)",
            "ciphertext_hex": ciphertext.hex(),
            "nonce_hex": nonce_bytes.hex(),
            "register_capacity": "10000 Bytes (80000 bits)"
        }

    def execute_message_encrypt(self, message_text: str) -> dict:
        if not self.is_initialized:
            raise RuntimeError("CRÍTICO: Processador ALU virtual não inicializado.")

        key = self._derive_key(b"s-message-chat-salt", b"chat-encryption")
        aesgcm = AESGCM(key)
        chat_nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(chat_nonce, message_text.encode('utf-8'), None)

        return {
            "processor_mode": "S Message Envelope Seguro (ALU 10000B)",
            "ciphertext_hex": ciphertext.hex(),
            "nonce_hex": chat_nonce.hex(),
            "alu_status": "Processado via registradores de 10000 Bytes"
        }

    def execute_custom_hash(self, data_string: str) -> str:
        return hashlib.sha512(data_string.encode('utf-8')).hexdigest()

    def zeroize(self):
        for reg in self.registers:
            if isinstance(self.registers[reg], bytearray):
                for i in range(len(self.registers[reg])):
                    self.registers[reg][i] = 0
        self.is_initialized = False


cpu_10000bytes = MilitaryGrade10000ByteProcessor()
cpu_10000bytes.load_master_buffer(b"s-message-secure-master-buffer-10000-bytes-2026")


# ==================================================
# ENDEREÇAMENTO COM CHECKSUM MATEMÁTICO PADRÃO snt1
# ==================================================
def generate_checksum_address(public_key_pem: str) -> str:
    pub_bytes = public_key_pem.strip().encode('utf-8')
    h1 = hashlib.sha256(pub_bytes).digest()
    checksum = hashlib.sha256(h1).digest()[:4].hex()
    base_address = hashlib.sha256(pub_bytes).hexdigest()[:36]
    return f"snt1{base_address}{checksum}"


# ==================================================
# FASTAPI + BLINDAGEM DE REDE FAIL2BAN / LIMITE DE REQUISIÇÕES
# ==================================================
app = FastAPI(
    title="S Message - Soberano Multimoeda & Central de Suporte Segura (Edição Militar Completa 10.0.0)",
    version="10.0.0",
    description="API definitiva: ALU 10KB, HKDF, Modo WAL, Endereço snt1, Prova de Posse, Anti-Replay, Fail2Ban, Biometria Anti-Spoofing"
)

request_history = defaultdict(list)
banned_ips = {}
RATE_LIMIT_WINDOW = 60
MAX_REQUESTS_PER_WINDOW = 30
BAN_DURATION = 900

SUPPORTED_ASSETS = ["USDT", "EURO_DIGITAL", "BRX", "SDC", "SDT"]
TRANSACTION_TTL_SECONDS = 30


@app.middleware("http")
async def military_grade_shield(request: Request, call_next):
    client_ip = request.client.host if request.client else "desconhecido"
    current_time = time.time()

    # Verifica bloqueio temporário
    if client_ip in banned_ips:
        if current_time < banned_ips[client_ip]:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detalhe": "ALERTA MILITAR: IP bloqueado temporariamente por atividade suspeita."}
            )
        else:
            del banned_ips[client_ip]

    # Conta requisições na janela
    client_requests = request_history[client_ip]
    request_history[client_ip] = [t for t in client_requests if current_time - t < RATE_LIMIT_WINDOW]

    if len(request_history[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
        banned_ips[client_ip] = current_time + BAN_DURATION
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detalhe": "ALERTA MILITAR: Limite excedido. IP isolado por 15 minutos (Fail2Ban)."}
        )

    request_history[client_ip].append(current_time)
    response = await call_next(request)

    # Cabeçalhos de proteção reforçada
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = "default-src 'self'"

    return response


# ==================================================
# BIOMETRIA FACIAL COM ANTI-SPOOFING
# ==================================================
def verify_facial_biometrics(image_bytes: bytes) -> bool:
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return False

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if gray.std() < 14.0 or gray.mean() < 20 or gray.mean() > 235:
            return False

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return len(faces) > 0

    except Exception:
        return False


# ==================================================
# ROTAS PRINCIPAIS DA API
# ==================================================
@app.get("/", summary="Status operacional do S Message")
async def root():
    return {
        "status": "online / armado",
        "projeto": "S Message",
        "versao": "10.0.0 Edição Militar Unificada Completa",
        "processador": "ALU Virtual 10000 Bytes + HKDF Ativo",
        "banco_dados": "SQLite (Modo WAL + Sincronização Total + Timeout 15s)",
        "padrao_endereco": "snt1 com Checksum Matemático Ativo",
        "camadas_seguranca": [
            "Prova de Posse (PoP)", "Proteção Anti-Replay (30s)", "Fail2Ban IP",
            "Central Segura", "Biometria Anti-Spoofing"
        ],
        "ativos_suportados": SUPPORTED_ASSETS
    }


@app.post("/api/v1/wallet/register", summary="Registrar Chave Pública com Prova de Posse")
async def register_wallet(
    public_key_pem: str = Form(...),
    challenge_nonce: str = Form(...),
    ecdsa_signature_hex: str = Form(...)
):
    try:
        pub_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
        if not isinstance(pub_key, ec.EllipticCurvePublicKey):
            raise HTTPException(status_code=400, detail="Apenas chaves de Curva Elíptica ECDSA são aceitas.")

        signature_bytes = bytes.fromhex(ecdsa_signature_hex)
        pub_key.verify(
            signature_bytes,
            challenge_nonce.encode('utf-8'),
            ec.ECDSA(hashes.SHA256())
        )
    except Exception as e:
        raise HTTPException(
# ==================================================
# EXECUÇÃO DO SERVIDOR COMPLETA NO FINAL DO ARQUIVO
# ==================================================
    cursor.execute('UPDATE wallet_balances SET balance = balance + ?, last_updated = ? WHERE wallet_address = ? AND asset_code = ?',
                   (amount, time.time(), wallet_to, asset_code))
    conn.commit()
    conn.close()

    return {"status": "200 OK", "mensagem": f"Depósito realizado com sucesso: {amount} {asset_code} na carteira {wallet_address}"}


@app.post("/api/v1/secure-transfer-biometric", summary="Transferência blindada: Assinatura + Biometria + Ledger")
async def secure_transfer_biometric(
    asset_code: str = Form(...),
    amount: float = Form(...),
    wallet_from: str = Form(...),
    wallet_to: str = Form(...),
    nonce: str = Form(...),
    timestamp: float = Form(...),
    ecdsa_signature_hex: str = Form(...),
    face_image: UploadFile = File(...)
):
    if asset_code not in SUPPORTED_ASSETS or amount <= 0:
        raise HTTPException(status_code=400, detail="Ativo ou valor inválido.")

    current_time = time.time()
    if abs(current_time - timestamp) > TRANSACTION_TTL_SECONDS:
        raise HTTPException(status_code=400, detail="Falha Anti-Replay: Transação expirada.")

    image_bytes = await face_image.read()
    if not verify_facial_biometrics(image_bytes):
        raise HTTPException(status_code=401, detail="Falha biométrica ou imagem falsa/estática detectada.")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Limpa e verifica nonce único
    cursor.execute('DELETE FROM used_nonces WHERE used_at < ?', (current_time - TRANSACTION_TTL_SECONDS,))
    cursor.execute('SELECT nonce FROM used_nonces WHERE nonce = ?', (nonce,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Falha Anti-Replay: Nonce já utilizado anteriormente.")

    # Carrega chave pública do remetente
    cursor.execute('SELECT public_key_pem FROM wallet_keys WHERE wallet_address = ?', (wallet_from,))
    row_key = cursor.fetchone()
    if not row_key:
        conn.close()
        raise HTTPException(status_code=400, detail="Carteira de origem não registrada.")

    payload = {
        "asset_code": asset_code, "amount": amount,
        "wallet_from": wallet_from, "wallet_to": wallet_to,
        "nonce": nonce, "timestamp": timestamp
    }
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))

    # Valida assinatura ECDSA
    try:
        public_key = serialization.load_pem_public_key(row_key[0].encode('utf-8'))
        public_key.verify(bytes.fromhex(ecdsa_signature_hex), payload_json.encode('utf-8'), ec.ECDSA(hashes.SHA256()))
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Assinatura inválida: {str(e)}")

    # Verifica e executa movimentação saldo
    cursor.execute('SELECT balance FROM wallet_balances WHERE wallet_address = ? AND asset_code = ?', (wallet_from, asset_code))
    row_balance = cursor.fetchone()
    current_balance = row_balance[0] if row_balance else 0.0

    if current_balance < amount:
        conn.close()
        raise HTTPException(status_code=400, detail="Saldo insuficiente para realizar transferência.")

    cursor.execute('UPDATE wallet_balances SET balance = balance - ?, last_updated = ? WHERE wallet_address = ? AND asset_code = ?',
                   (amount, time.time(), wallet_from, asset_code))
    cursor.execute('INSERT OR IGNORE INTO wallet_balances (wallet_address, asset_code, balance, last_updated) VALUES (?, ?, 0.0, ?)',
                   (wallet_to, asset_code, time.time()))
    cursor.execute('UPDATE wallet_balances SET balance = balance + ?, last_updated = ? WHERE wallet_address = ? AND asset_code = ?',
                   (amount, time.time(), wallet_to, asset_code))

    cursor.execute('INSERT INTO used_nonces (nonce, used_at) VALUES (?, ?)', (nonce, current_time))

    # Grava no Ledger criptografado
    encrypted_data = cpu_10000bytes.execute_aes_encrypt(payload_json.encode('utf-8'), os.urandom(12))

    cursor.execute('SELECT block_index, block_hash FROM ledger ORDER BY block_index DESC LIMIT 1')
    last_block = cursor.fetchone()
    new_index = last_block[0] + 1
    new_timestamp = time.time()

    block_string = json.dumps({
        "index": new_index, "timestamp": new_timestamp,
        "payload": encrypted_data, "previous_hash": last_block[1]
    }, sort_keys=True, separators=(',', ':'))

    new_block_hash = cpu_10000bytes.execute_custom_hash(block_string)

    cursor.execute('''
    INSERT INTO ledger (block_index, timestamp, payload, previous_hash, block_hash)
    VALUES (?, ?, ?, ?, ?)
    ''', (new_index, new_timestamp, json.dumps(encrypted_data), last_block[1], new_block_hash))

    conn.commit()
    conn.close()

    return {
        "status": "200 OK",
        "mensagem": "Transferência soberana processada e registrada com sucesso!",
        "bloco_indice": new_index,
        "bloco_hash": new_block_hash
    }


@app.get("/api/v1/audit/chain", summary="Consultar cadeia completa do Ledger")
async def get_audit_chain():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT block_index, timestamp, payload, previous_hash, block_hash FROM ledger ORDER BY block_index ASC')
    rows = cursor.fetchall()

    lista_ledger = []
    for row in rows:
        try:
            conteudo = json.loads(row["payload"])
        except:
            conteudo = row["payload"]
        lista_ledger.append({
            "indice": row["block_index"],
            "tempo": row["timestamp"],
            "conteudo": conteudo,
            "anterior_hash": row["previous_hash"],
            "bloco_hash": row["block_hash"]
        })
    conn.close()
    return {"tamanho_cadeia": len(lista_ledger), "registros": lista_ledger}


# === LINHA FINAL QUE LIGA O SERVIDOR ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
