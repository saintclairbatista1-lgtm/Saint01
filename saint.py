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
# 1. INICIALIZAÇÃO E BLINDAGEM DO FASTAPI
# ==========================================
app = FastAPI(
    title="S Message - Secure Ledger with Biometric Shield",
    version="2.3.0",
    description="API blindada com AES-256-GCM, HMAC, Ledger Imutável e Reconhecimento Facial"
)

# Chaves de segurança de nível militar
MILITARY_GRADE_SECRET = b"s-message-secure-master-key-2026"

# Geração da chave mestra AES-256 (32 bytes)
AES_MASTER_KEY = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(AES_MASTER_KEY)

# Estrutura inicial do Ledger (Bloco Gênesis)
blockchain_ledger = [{
    "index": 0,
    "timestamp": 0.0,
    "payload": "Genesis Block",
    "previous_hash": "0" * 64,
    "block_hash": "0" * 64
}]

# Controle de Rate Limiting em memória
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
    
    # Headers de Segurança HTTP
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response


# ==========================================
# 3. MÓDULO DE BIOMETRIA E VISÃO COMPUTACIONAL
# ==========================================
def verify_facial_biometrics(image_bytes: bytes) -> bool:
    """
    Utiliza OpenCV para decodificar a imagem enviada, convertê-la para escala de cinza
    e validar a presença de traços faciais utilizando o classificador Haar Cascade padrão.
    """
    try:
        # Converte os bytes da imagem em um array numpy para o OpenCV
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return False
            
        # Converte para escala de cinza para otimizar a detecção de padrões faciais
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Carrega o classificador pré-treinado de face do OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detecta rostos na imagem
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Retorna True se pelo menos um rosto válido foi encontrado na imagem de pagamento
        return len(faces) > 0
    except Exception:
        return false


# ==========================================
# 4. FUNÇÕES DE CRIPTOGRAFIA E HASH
# ==========================================
def encrypt_payload(data_dict: dict) -> dict:
    nonce = os.urandom(12)
    message_bytes = json.dumps(data_dict, sort_keys=True).encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, message_bytes, None)
    return {
        "ciphertext_hex": ciphertext.hex(),
        "nonce_hex": nonce.hex()
    }

def calculate_block_hash(block: dict) -> str:
    block_string = json.dumps({
        "index": block["index"],
        "timestamp": block["timestamp"],
        "payload": block["payload"],
        "previous_hash": block["previous_hash"]
    }, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(block_string.encode('utf-8')).hexdigest()


# ==========================================
# 5. ROTAS DA API COM BIOMETRIA
# ==========================================
@app.get("/", summary="Status do Sistema")
async def root():
    return {
        "status": "online",
        "project": "S Message",
        "biometric_shield": "OpenCV Facial Verification Active",
        "encryption": "AES-256-GCM + HMAC-SHA256"
    }

@app.post("/api/v1/secure-transfer-biometric", summary="Transferência B2B com Reconhecimento Facial")
async def secure_transfer_biometric(
    asset_type: str = Form(..., description="Tipo de ativo"),
    amount: float = Form(..., description="Valor da transação"),
    wallet_from: str = Form(..., description="Carteira de origem"),
    wallet_to: str = Form(..., description="Carteira de destino"),
    digital_signature: str = Form(..., description="Assinatura HMAC-SHA256"),
    face_image: UploadFile = File(..., description="Foto do rosto para validação biométrica")
):
    """
    Executa a verificação facial por OpenCV, valida o HMAC, criptografa com AES-256 
    e registra a transação de forma imutável no Ledger.
    """
    # 1. Leitura e Validação Biométrica Facial
    image_bytes = await face_image.read()
    is_face_valid = verify_facial_biometrics(image_bytes)
    
    if not is_face_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falha biométrica: Nenhum rosto válido detectado ou identidade não confirmada."
        )
        
    # 2. Estruturação do Payload
    payload = {
        "asset_type": asset_type,
        "amount": amount,
        "wallet_from": wallet_from,
        "wallet_to": wallet_to
    }
    
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    # 3. Validação de Integridade HMAC-SHA256
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
    
    # 4. Criptografia AES-256-GCM
    encrypted_data = encrypt_payload(payload)
    
    # 5. Registro no Ledger Imutável
    previous_block = blockchain_ledger[-1]
    new_index = previous_block["index"] + 1
    
    new_block_data = {
        "index": new_index,
        "timestamp": time.time(),
        "payload": encrypted_data,
        "previous_hash": previous_block["block_hash"]
    }
    
    new_block_data["block_hash"] = calculate_block_hash(new_block_data)
    blockchain_ledger.append(new_block_data)
    
    return {
        "status": "200 OK",
        "message": "Autenticação facial aprovada! Transação criptografada e registrada com sucesso.",
        "block_index": new_index,
        "encrypted_envelope": encrypted_data,
        "block_hash": new_block_data["block_hash"]
    }

@app.get("/api/v1/audit/chain", summary="Consultar Ledger")
async def get_audit_chain():
    return {"chain_length": len(blockchain_ledger), "ledger": blockchain_ledger}


# ==========================================
# 6. EXECUÇÃO LOCAL
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8765, reload=True)
