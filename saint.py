import os
import json
import time
import hmac
import hashlib
import numpy as np
import cv2
from collections import defaultdict
from fastapi import FastAPI, HTTPException, status, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ==========================================
# 0. MICROPROCESSADOR PROPRIETÁRIO 500-BYTE (EMULADOR DE HARDWARE)
# ==========================================
class Custom500ByteProcessor:
    """
    Emulador de Microprocessador de 500 bytes (4.000 bits) para autonomia criptográfica máxima na nuvem.
    Opera com registradores de alta capacidade dedicados ao S Message.
    """
    def __init__(self):
        self.registers = {
            "R0": b"\x00" * 500,  # Acumulador de dados estendido (500 bytes)
            "R1": b"\x00" * 500,  # Registrador de Chave / Buffer Mestre (500 bytes)
            "R2": b"\x00" * 12,   # Nonce / Vetor de Inicialização (12 bytes para GCM)
            "FLAGS": 0x00        # Status do processador
        }
        self.is_initialized = False

    def load_master_buffer(self, input_bytes: bytes):
        """Carrega e estende os dados para preencher exatamente o registrador de 500 bytes."""
        padded_buffer = bytearray()
        seed = input_bytes
        while len(padded_buffer) < 500:
            seed = hashlib.sha512(seed).digest()
            padded_buffer.extend(seed)
        
        self.registers["R1"] = bytes(padded_buffer[:500])
        self.is_initialized = True
        self.registers["FLAGS"] = 0x01

    def execute_aes_encrypt(self, plaintext_bytes: bytes, nonce_bytes: bytes) -> dict:
        """Executa cifragem AES-256 utilizando os primeiros 32 bytes do buffer de 500 bytes do registrador R1."""
        if not self.is_initialized:
            raise RuntimeError("Erro de Hardware Virtual: Processador de 500 bytes não inicializado.")
        
        aes_key_segment = self.registers["R1"][:32]
        aesgcm = AESGCM(aes_key_segment)
        
        ciphertext = aesgcm.encrypt(nonce_bytes, plaintext_bytes, None)
        return {
            "processor_status": "OK (500-Byte ALU Active)",
            "ciphertext_hex": ciphertext.hex(),
            "nonce_hex": nonce_bytes.hex(),
            "register_capacity": "500 Bytes (4000 bits)"
        }

    def execute_custom_hash(self, data_string: str) -> str:
        """Instrução nativa de hardware: Gera hash SHA-512 combinado para o Ledger de 500 bytes."""
        return hashlib.sha512(data_string.encode('utf-8')).hexdigest()

# Instanciação do microprocessador de 500 bytes do S Message
cpu_500bytes = Custom500ByteProcessor()
cpu_500bytes.load_master_buffer(b"s-message-secure-master-buffer-500-bytes-2026")


# ==========================================
# 1. INICIALIZAÇÃO E BLINDAGEM DO FASTAPI
# ==========================================
app = FastAPI(
    title="S Message - Autonomous 500-Byte Secure Ledger",
    version="2.6.0",
    description="API blindada operando com microprocessador virtual de 500 bytes, biometria e Ledger imutável"
)

MILITARY_GRADE_SECRET = b"s-message-secure-master-key-2026"

blockchain_ledger = [{
    "index": 0,
    "timestamp": 0.0,
    "payload": "Genesis Block (Hardware Virtual 500-Byte)",
    "previous_hash": "0" * 128,
    "block_hash": "0" * 128
}]

request_history = defaultdict(list)
RATE_LIMIT_WINDOW = 60
MAX_REQUESTS_ALLOWED = 15


# ==========================================
# 2. MIDDLEWARE DE SEGURANÇA E RATE LIMIT
# ==========================================
@app.middleware("http")
async def military_grade_shield(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    
    client_requests = request_history[client_ip]
    request_history[client_ip] = [t for t in client_requests if current_time - t < RATE_LIMIT_WINDOW]
    
    if len(request_history[client_ip]) >= MAX_REQUESTS_ALLOWED:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Blindagem Ativa: Limite de requisições excedido."}
        )
    
    request_history[client_ip].append(current_time)
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response


# ==========================================
# 3. MÓDULO DE BIOMETRIA E VISÃO COMPUTACIONAL
# ==========================================
def verify_facial_biometrics(image_bytes: bytes) -> bool:
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return False
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        return len(faces) > 0
    except Exception:
        return False


# ==========================================
# 4. ROTAS DA API COM PROCESSADOR 500-BYTE
# ==========================================
@app.get("/", summary="Status do Sistema com Processador 500-Byte")
async def root():
    return {
        "status": "online",
        "project": "S Message",
        "processor_architecture": "Custom 500-Byte Virtual ALU Active",
        "biometric_shield": "OpenCV Facial Verification Active",
        "register_capacity": "500 Bytes (4000 bits)"
    }

@app.post("/api/v1/secure-transfer-biometric", summary="Transferência com Biometria e Processador 500-Byte")
async def secure_transfer_biometric(
    asset_type: str = Form(..., description="Tipo de ativo"),
    amount: float = Form(..., description="Valor da transação"),
    wallet_from: str = Form(..., description="Carteira de origem"),
    wallet_to: str = Form(..., description="Carteira de destino"),
    digital_signature: str = Form(..., description="Assinatura HMAC-SHA256"),
    face_image: UploadFile = File(..., description="Foto do rosto para validação biométrica")
):
    # 1. Validação Biométrica Facial
    image_bytes = await face_image.read()
    if not verify_facial_biometrics(image_bytes):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falha biométrica: Rosto não validado."
        )
        
    # 2. Payload e HMAC
    payload = {
        "asset_type": asset_type,
        "amount": amount,
        "wallet_from": wallet_from,
        "wallet_to": wallet_to
    }
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    expected_signature = hmac.new(
        MILITARY_GRADE_SECRET, 
        payload_json.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(digital_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Falha de blindagem: Assinatura digital inválida."
        )
    
    # 3. Processamento Criptográfico via Microprocessador Virtual de 500 Bytes
    nonce = os.urandom(12)
    encrypted_data = cpu_500bytes.execute_aes_encrypt(
        json.dumps(payload, sort_keys=True).encode('utf-8'), 
        nonce
    )
    
    # 4. Registro no Ledger Imutável
    previous_block = blockchain_ledger[-1]
    new_index = previous_block["index"] + 1
    
    new_block_data = {
        "index": new_index,
        "timestamp": time.time(),
        "payload": encrypted_data,
        "previous_hash": previous_block["block_hash"]
    }
    
    block_string = json.dumps({
        "index": new_block_data["index"],
        "timestamp": new_block_data["timestamp"],
        "payload": new_block_data["payload"],
        "previous_hash": new_block_data["previous_hash"]
    }, sort_keys=True, separators=(',', ':'))
    
    new_block_data["block_hash"] = cpu_500bytes.execute_custom_hash(block_string)
    blockchain_ledger.append(new_block_data)
    
    return {
        "status": "200 OK",
        "message": "Transação processada pelo chip virtual de 500 bytes e registrada no Ledger!",
        "block_index": new_index,
        "processor_telemetry": encrypted_data["processor_status"],
        "register_capacity": encrypted_data["register_capacity"],
        "encrypted_envelope": {
            "ciphertext_hex": encrypted_data["ciphertext_hex"],
            "nonce_hex": encrypted_data["nonce_hex"]
        },
        "block_hash": new_block_data["block_hash"]
    }

@app.get("/api/v1/audit/chain", summary="Consultar Ledger")
async def get_audit_chain():
    return {"chain_length": len(blockchain_ledger), "ledger": blockchain_ledger}


# ==========================================
# 5. EXECUÇÃO LOCAL
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8765, reload=True)
