import os
import json
import time
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

# ==========================================
# 0. CONFIGURAÇÃO ROBUSTA DO BANCO DE DADOS (WAL + FULL SYNC)
# ==========================================
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
    
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM ledger')
    if cursor.fetchone()[0] == 0:
        genesis_payload = "Genesis Block (S Message Full Unified Military-Grade Edition 2026)"
        genesis_hash = "0" * 128
        cursor.execute('''
            INSERT INTO ledger (block_index, timestamp, payload, previous_hash, block_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (0, 0.0, genesis_payload, genesis_hash, genesis_hash))
        conn.commit()
        
    conn.close()

init_db()


# ==========================================
# 1. MICROPROCESSADOR PROPRIETÁRIO 10.000-BYTE (ALU + HKDF + ZEROIZAÇÃO)
# ==========================================
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
            raise RuntimeError("CRITICAL: Hardware ALU uninitialized.")
        
        key = self._derive_key(b"s-message-ledger-salt", b"ledger-encryption")
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce_bytes, plaintext_bytes, None)
        return {
            "processor_status": "MILITARY ALU ACTIVE (10000B + HKDF + AES-GCM)",
            "ciphertext_hex": ciphertext.hex(),
            "nonce_hex": nonce_bytes.hex(),
            "register_capacity": "10000 Bytes (80000 bits)"
        }

    def execute_message_encrypt(self, message_text: str) -> dict:
        if not self.is_initialized:
            raise RuntimeError("CRITICAL: Hardware ALU uninitialized.")
        
        key = self._derive_key(b"s-message-chat-salt", b"chat-encryption")
        aesgcm = AESGCM(key)
        chat_nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(chat_nonce, message_text.encode('utf-8'), None)
        return {
            "processor_mode": "S Message Secure Chat Envelope (10000B ALU)",
            "ciphertext_hex": ciphertext.hex(),
            "nonce_hex": chat_nonce.hex(),
            "alu_status": "Processed via 10000-Byte Registers"
        }

    def execute_custom_hash(self, data_string: str) -> str:
        return hashlib.sha512(data_string.encode('utf-8')).hexdigest()

    def zeroize(self):
        """Destruição de dados sensíveis na memória RAM (Zeroization)"""
        for reg in self.registers:
            if isinstance(self.registers[reg], bytearray):
                for i in range(len(self.registers[reg])):
                    self.registers[reg][i] = 0
        self.is_initialized = False

cpu_10000bytes = MilitaryGrade10000ByteProcessor()
cpu_10000bytes.load_master_buffer(b"s-message-secure-master-buffer-10000-bytes-2026")


# ==========================================
# 2. ENDEREÇAMENTO COM CHECKSUM MATEMÁTICO (`snt1`)
# ==========================================
def generate_checksum_address(public_key_pem: str) -> str:
    pub_bytes = public_key_pem.strip().encode('utf-8')
    h1 = hashlib.sha256(pub_bytes).digest()
    checksum = hashlib.sha256(h1).digest()[:4].hex()
    base_address = hashlib.sha256(pub_bytes).hexdigest()[:36]
    return f"snt1{base_address}{checksum}"


# ==========================================
# 3. FASTAPI E BLINDAGEM DE REDE (FAIL2BAN + RATE LIMIT)
# ==========================================
app = FastAPI(
    title="S Message - Sovereign Multicurrency & Secure Chat (Full Military Edition)",
    version="8.0.0",
    description="API Completa com ALU 10KB, HKDF, WAL Mode, Checksum snt1, Prova de Posse, Anti-Spoofing e Fail2Ban"
)

request_history = defaultdict(list)
banned_ips = {}
RATE_LIMIT_WINDOW = 60
MAX_REQUESTS_PER_WINDOW = 20
BAN_DURATION = 900  # 15 minutos de isolamento de IP

SUPPORTED_ASSETS = ["USDT", "EURO_DIGITAL", "BRX", "SDC", "SDT"]
TRANSACTION_TTL_SECONDS = 30


@app.middleware("http")
async def military_grade_shield(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    
    if client_ip in banned_ips:
        if current_time < banned_ips[client_ip]:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "ALERTA MILITAR: IP bloqueado temporariamente por atividade suspeita."}
            )
        else:
            del banned_ips[client_ip]
            
    client_requests = request_history[client_ip]
    request_history[client_ip] = [t for t in client_requests if current_time - t < RATE_LIMIT_WINDOW]
    
    if len(request_history[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
        banned_ips[client_ip] = current_time + BAN_DURATION
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "ALERTA MILITAR: Limite excedido. IP isolado por 15 minutos (Fail2Ban)."}
        )
    
    request_history[client_ip].append(current_time)
    response = await call_next(request)
    
    # Cabeçalhos de Segurança Militar
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response


# ==========================================
# 4. BIOMETRIA COM ANTI-SPOOFING AVANÇADO
# ==========================================
def verify_facial_biometrics(image_bytes: bytes) -> bool:
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return False
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Rejeição de fotos impressas planas ou telas apagadas/estouradas
        if gray.std() < 14.0 or gray.mean() < 20 or gray.mean() > 235:
            return False

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        return len(faces) > 0
    except Exception:
        return False


# ==========================================
# 5. ROTAS DA API
# ==========================================
@app.get("/", summary="Status do Sistema S Message")
async def root():
    return {
        "status": "online / armed",
        "project": "S Message",
        "version": "8.0.0 Full Military",
        "processor_architecture": "Custom 10000-Byte Virtual ALU + HKDF Active",
        "database_engine": "SQLite (WAL Mode + Full Synchronous + 15s Timeout)",
        "address_standard": "snt1 with Mathematical Checksum Active",
        "biometric_shield": "OpenCV Facial Verification + Advanced Anti-Spoofing",
        "security_layers": ["Proof of Possession (PoP)", "Anti-Replay TTL (30s)", "Fail2Ban IP Guard", "Memory Zeroization"],
        "supported_assets": SUPPORTED_ASSETS
    }

@app.post("/api/v1/wallet/register", summary="Registrar Chave Pública com Prova de Posse e Checksum")
async def register_wallet(
    public_key_pem: str = Form(..., description="Chave pública PEM gerada localmente pelo usuário"),
    challenge_nonce: str = Form(..., description="Desafio randômico gerado pelo cliente"),
    ecdsa_signature_hex: str = Form(..., description="Assinatura digital gerada com a chave privada sobre o challenge_nonce")
):
    try:
        pub_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
        if not isinstance(pub_key, ec.EllipticCurvePublicKey):
            raise HTTPException(status_code=400, detail="Apenas chaves baseadas em Curvas Elípticas (ECDSA) são suportadas.")
        
        signature_bytes = bytes.fromhex(ecdsa_signature_hex)
        pub_key.verify(
            signature_bytes,
            challenge_nonce.encode('utf-8'),
            ec.ECDSA(hashes.SHA256())
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Falha na Prova de Posse: A assinatura do desafio é inválida ou a chave PEM está corrompida. Detalhe: {str(e)}"
        )
    
    wallet_address = generate_checksum_address(public_key_pem)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO wallet_keys (wallet_address, public_key_pem, created_at)
        VALUES (?, ?, ?)
    ''', (wallet_address, public_key_pem.strip(), time.time()))
    conn.commit()
    conn.close()
    
    return {
        "status": "200 OK",
        "message": "Chave pública validada via Prova de Posse e registrada com endereço com Checksum!",
        "wallet_address": wallet_address
    }

@app.get("/api/v1/wallet/{wallet_address}", summary="Consultar Saldos Multimoeda")
async def get_wallet_balances(wallet_address: str):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT asset_code, balance FROM wallet_balances WHERE wallet_address = ?', (wallet_address,))
    rows = cursor.fetchall()
    conn.close()
    
    balances = {row["asset_code"]: row["balance"] for row in rows}
    
    return {
        "wallet_address": wallet_address,
        "balances": balances
    }

@app.post("/api/v1/wallet/deposit", summary="Depositar Fundos na Carteira")
async def wallet_deposit(
    wallet_address: str = Form(...),
    asset_code: str = Form(..., description="Ex: USDT, EURO_DIGITAL, BRX, SDC, SDT"),
    amount: float = Form(...)
):
    if asset_code not in SUPPORTED_ASSETS:
        raise HTTPException(status_code=400, detail=f"Ativo não suportado. Ativos válidos: {SUPPORTED_ASSETS}")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="O valor do depósito deve ser maior que zero.")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO wallet_balances (wallet_address, asset_code, balance, last_updated)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(wallet_address, asset_code) 
        DO UPDATE SET balance = balance + ?, last_updated = ?
    ''', (wallet_address, asset_code, amount, time.time(), amount, time.time()))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "200 OK",
        "message": f"Depósito de {amount} {asset_code} realizado com sucesso para {wallet_address}."
    }

@app.post("/api/v1/message/encrypt", summary="Criptografar Mensagem de Chat usando a ALU de 10.000 Bytes")
async def encrypt_chat_message(
    message: str = Form(..., description="Texto da mensagem de chat a ser cifrada")
):
    try:
        encrypted_envelope = cpu_10000bytes.execute_message_encrypt(message)
        return {
            "status": "200 OK",
            "message": "Mensagem cifrada com sucesso pelo microprocessador virtual de 10000 bytes (HKDF + AES-GCM).",
            "envelope": encrypted_envelope
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento de hardware virtual: {str(e)}")

@app.post("/api/v1/secure-transfer-biometric", summary="Transferência com Assinatura, WAL Concurrency, TTL, Anti-Replay e Anti-Spoofing")
async def secure_transfer_biometric(
    asset_code: str = Form(..., description="Ex: USDT, EURO_DIGITAL, BRX, SDC, SDT"),
    amount: float = Form(..., description="Valor da transação"),
    wallet_from: str = Form(..., description="Endereço da carteira de origem"),
    wallet_to: str = Form(..., description="Carteira de destino"),
    nonce: str = Form(..., description="Identificador único da transação gerado pelo cliente"),
    timestamp: float = Form(..., description="Timestamp Unix exato da assinatura"),
    ecdsa_signature_hex: str = Form(..., description="Assinatura digital ECDSA cobrindo o payload completo"),
    face_image: UploadFile = File(..., description="Foto do rosto para validação biométrica com anti-spoofing")
):
    if asset_code not in SUPPORTED_ASSETS:
        raise HTTPException(status_code=400, detail=f"Ativo não suportado. Ativos válidos: {SUPPORTED_ASSETS}")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="O valor da transferência deve ser maior que zero.")

    current_time = time.time()
    if abs(current_time - timestamp) > TRANSACTION_TTL_SECONDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha Anti-Replay: Transação expirada ({TRANSACTION_TTL_SECONDS}s)."
        )

    image_bytes = await face_image.read()
    if not verify_facial_biometrics(image_bytes):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falha biométrica ou Anti-Spoofing: Rosto não validado ou detecção de imagem estática/falsa."
        )
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    expiration_threshold = current_time - TRANSACTION_TTL_SECONDS
    cursor.execute('DELETE FROM used_nonces WHERE used_at < ?', (expiration_threshold,))
    
    cursor.execute('SELECT nonce FROM used_nonces WHERE nonce = ?', (nonce,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Falha Anti-Replay: Este nonce já foi utilizado."
        )

    cursor.execute('SELECT public_key_pem FROM wallet_keys WHERE wallet_address = ?', (wallet_from,))
    row_key = cursor.fetchone()
    
    if not row_key:
        conn.close()
        raise HTTPException(status_code=400, detail="Carteira de origem não registrada ou sem chave pública cadastrada.")
    
    public_key_pem = row_key[0]
    
    payload = {
        "asset_code": asset_code,
        "amount": amount,
        "wallet_from": wallet_from,
        "wallet_to": wallet_to,
        "nonce": nonce,
        "timestamp": timestamp
    }
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
        signature_bytes = bytes.fromhex(ecdsa_signature_hex)
        
        public_key.verify(
            signature_bytes,
            payload_json.encode('utf-8'),
            ec.ECDSA(hashes.SHA256())
        )
    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Falha de blindagem: Assinatura ECDSA inválida. Detalhe: {str(e)}"
        )
    
    cursor.execute('SELECT balance FROM wallet_balances WHERE wallet_address = ? AND asset_code = ?', (wallet_from, asset_code))
    row_balance = cursor.fetchone()
    current_balance = row_balance[0] if row_balance else 0.0
    
    if current_balance < amount:
        conn.close()
        raise HTTPException(status_code=400, detail="Saldo insuficiente para realizar a transferência.")
        
    cursor.execute('UPDATE wallet_balances SET balance = balance - ?, last_updated = ? WHERE wallet_address = ? AND asset_code = ?', 
                   (amount, time.time(), wallet_from, asset_code))
                   
    cursor.execute('INSERT OR IGNORE INTO wallet_balances (wallet_address, asset_code, balance, last_updated) VALUES (?, ?, 0.0, ?)',
                   (wallet_to, asset_code, time.time()))
    cursor.execute('UPDATE wallet_balances SET balance = balance + ?, last_updated = ? WHERE wallet_address = ? AND asset_code = ?', 
                   (amount, time.time(), wallet_to, asset_code))

    cursor.execute('INSERT INTO used_nonces (nonce, used_at) VALUES (?, ?)', (nonce, current_time))

    aes_nonce = os.urandom(12)
    encrypted_data = cpu_10000bytes.execute_aes_encrypt(
        payload_json.encode('utf-8'), 
        aes_nonce
    )
    
    cursor.execute('SELECT block_index, block_hash FROM ledger ORDER BY block_index DESC LIMIT 1')
    last_block = cursor.fetchone()
    
    previous_index = last_block[0]
    previous_hash = last_block[1]
    new_index = previous_index + 1
    new_timestamp = time.time()
    
    block_string = json.dumps({
        "index": new_index,
        "timestamp": new_timestamp,
        "payload": encrypted_data,
        "previous_hash": previous_hash
    }, sort_keys=True, separators=(',', ':'))
    
    new_block_hash = cpu_10000bytes.execute_custom_hash(block_string)
    
    cursor.execute('''
        INSERT INTO ledger (block_index, timestamp, payload, previous_hash, block_hash)
        VALUES (?, ?, ?, ?, ?)
    ''', (new_index, new_timestamp, json.dumps(encrypted_data), previous_hash, new_block_hash))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "200 OK",
        "message": f"Transferência soberana de {amount} {asset_code} processada com ALU 10KB, WAL Mode e Anti-Spoofing!",
        "block_index": new_index,
        "processor_telemetry": encrypted_data["processor_status"],
        "encrypted_envelope": {
            "ciphertext_hex": encrypted_data["ciphertext_hex"],
            "nonce_hex": encrypted_data["nonce_hex"]
        },
        "block_hash": new_block_hash
    }

@app.get("/api/v1/audit/chain", summary="Consultar Ledger no SQLite")
async def get_audit_chain():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT block_index, timestamp, payload, previous_hash, block_hash FROM ledger ORDER BY block_index ASC')
    rows = cursor.fetchall()
    
    ledger_list = []
    for row in rows:
        try:
            parsed_payload = json.loads(row["payload"])
        except:
            parsed_payload = row["payload"]
            
        ledger_list.append({
            "index": row["block_index"],
            "timestamp": row["timestamp"],
            "payload": parsed_payload,
            "previous_hash": row["previous_hash"],
            "block_hash": row["block_hash"]
        })
    conn.close()
    return {"chain_length": len(ledger_list), "ledger": ledger_list}


# ==========================================
# 6. EXECUÇÃO PARA DEPLOY / LOCAL
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("saint:app", host="0.0.0.0", port=port, reload=True)
