import os
import json
import time
import hmac
import hashlib
from collections import defaultdict
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ==========================================
# 1. INICIALIZAÇÃO E BLINDAGEM DO FASTAPI
# ==========================================
app = FastAPI(
    title="S Message - Military Grade Secure Ledger",
    version="2.2.0",
    description="API blindada com AES-256-GCM, HMAC, Ledger Imutável e Rate Limiting"
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

# Controle de Rate Limiting em memória (IP -> lista de timestamps de requisições)
request_history = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # Janela de 60 segundos
MAX_REQUESTS_ALLOWED = 10  # Máximo de 10 requisições por janela por IP


# ==========================================
# 2. MIDDLEWARE DE HEADERS DE SEGURANÇA E RATE LIMIT
# ==========================================
@app.middleware("http")
async def military_grade_shield(request: Request, call_next):
    """
    Middleware de blindagem: injeta headers de segurança de nível militar 
    e aplica controle rigoroso de Rate Limiting contra ataques de força bruta.
    """
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    
    # 1. Execução do Rate Limiting
    client_requests = request_history[client_ip]
    # Remove requisições fora da janela de tempo
    request_history[client_ip] = [t for t in client_requests if current_time - t < RATE_LIMIT_WINDOW]
    
    if len(request_history[client_ip]) >= MAX_REQUESTS_ALLOWED:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Blindagem Ativa: Limite de requisições excedido. IP temporariamente limitado."}
        )
    
    request_history[client_ip].append(current_time)
    
    # 2. Processamento da requisição
    response = await call_next(request)
    
    # 3. Injeção de Headers de Segurança (Blindagem contra XSS, Clickjacking, etc.)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response


# ==========================================
# 3. MODELOS DE DADOS (PYDANTIC)
# ==========================================
class Transaction(BaseModel):
    asset_type: str = Field(..., description="Tipo de ativo sendo transferido")
    amount: float = Field(..., gt=0, description="Valor da transação")
    wallet_from: str = Field(..., description="Carteira de origem")
    wallet_to: str = Field(..., description="Carteira de destino")
    digital_signature: str = Field(..., description="Assinatura HMAC-SHA256")


# ==========================================
# 4. MÓDULO DE CRIPTOGRAFIA E HASH
# ==========================================
def encrypt_payload(data_dict: dict) -> dict:
    """Criptografa um dicionário utilizando AES-256-GCM com Nonce exclusivo."""
    nonce = os.urandom(12)
    message_bytes = json.dumps(data_dict, sort_keys=True).encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, message_bytes, None)
    return {
        "ciphertext_hex": ciphertext.hex(),
        "nonce_hex": nonce.hex()
    }

def calculate_block_hash(block: dict) -> str:
    """Calcula o hash SHA-256 do bloco para o Ledger."""
    block_string = json.dumps({
        "index": block["index"],
        "timestamp": block["timestamp"],
        "payload": block["payload"],
        "previous_hash": block["previous_hash"]
    }, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(block_string.encode('utf-8')).hexdigest()


# ==========================================
# 5. ROTAS DA API BLINDADA
# ==========================================
@app.get("/", summary="Status da Blindagem")
async def root():
    return {
        "status": "online",
        "project": "S Message",
        "shield": "Military Grade Active",
        "encryption": "AES-256-GCM + HMAC-SHA256"
    }

@app.post("/api/v1/secure-transfer", summary="Transferência Blindada B2B")
async def secure_transfer(transaction: Transaction):
    """Valida HMAC, criptografa com AES-256 e grava no Ledger de forma imutável."""
    payload = {
        "asset_type": transaction.asset_type,
        "amount": transaction.amount,
        "wallet_from": transaction.wallet_from,
        "wallet_to": transaction.wallet_to
    }
    
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    # 1. Validação de Integridade HMAC-SHA256
    expected_signature = hmac.new(
        MILITARY_GRADE_SECRET, 
        payload_json.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(transaction.digital_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Falha de blindagem: Assinatura digital inválida ou adulterada."
        )
    
    # 2. Criptografia AES-256-GCM
    encrypted_data = encrypt_payload(payload)
    
    # 3. Ledger Imutável
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
        "message": "Transação blindada, criptografada e registrada com sucesso!",
        "block_index": new_index,
        "encrypted_envelope": encrypted_data,
        "block_hash": new_block_data["block_hash"]
    }

@app.get("/api/v1/audit/chain", summary="Consultar Ledger Blindado")
async def get_audit_chain():
    return {"chain_length": len(blockchain_ledger), "ledger": blockchain_ledger}


# ==========================================
# 6. EXECUÇÃO LOCAL
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8765, reload=True)
