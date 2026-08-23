import os
import json
import time
import hmac
import hashlib
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ==========================================
# 1. INICIALIZAÇÃO DA APLICAÇÃO FASTAPI
# ==========================================
app = FastAPI(
    title="S Message - Secure Ledger & Cryptography",
    version="2.1.0",
    description="API com criptografia AES-256-GCM, validação HMAC e Ledger Imutável"
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


# ==========================================
# 2. MODELOS DE DADOS (PYDANTIC)
# ==========================================
class Transaction(BaseModel):
    asset_type: str = Field(..., description="Tipo de ativo sendo transferido")
    amount: float = Field(..., gt=0, description="Valor da transação")
    wallet_from: str = Field(..., description="Carteira de origem")
    wallet_to: str = Field(..., description="Carteira de destino")
    digital_signature: str = Field(..., description="Assinatura HMAC-SHA256")


# ==========================================
# 3. MÓDULO DE CRIPTOGRAFIA AES-256-GCM
# ==========================================
def encrypt_payload(data_dict: dict) -> dict:
    """
    Criptografa um dicionário utilizando AES-256-GCM.
    Retorna o texto cifrado e o Nonce em formato hexadecimal.
    """
    nonce = os.urandom(12)  # 12 bytes recomendado para GCM
    message_bytes = json.dumps(data_dict, sort_keys=True).encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, message_bytes, None)
    return {
        "ciphertext_hex": ciphertext.hex(),
        "nonce_hex": nonce.hex()
    }

def decrypt_payload(ciphertext_hex: str, nonce_hex: str) -> dict:
    """
    Descriptografa dados protegidos por AES-256-GCM a partir de strings hexadecimais.
    """
    try:
        nonce = bytes.fromhex(nonce_hex)
        ciphertext = bytes.fromhex(ciphertext_hex)
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(decrypted_bytes.decode('utf-8'))
    except Exception as e:
        raise ValueError(f"Falha na descriptografia AES-GCM: {str(e)}")

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
# 4. ROTAS DA API
# ==========================================
@app.get("/", summary="Status do Servidor")
async def root():
    return {"status": "online", "project": "S Message", "encryption": "AES-256-GCM Active"}

@app.post("/api/v1/secure-transfer", summary="Transferência com HMAC e AES-256")
async def secure_transfer(transaction: Transaction):
    """Valida a assinatura, encripta os dados com AES-256 e grava no Ledger."""
    payload = {
        "asset_type": transaction.asset_type,
        "amount": transaction.amount,
        "wallet_from": transaction.wallet_from,
        "wallet_to": transaction.wallet_to
    }
    
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    # 1. Validação HMAC-SHA256
    expected_signature = hmac.new(
        MILITARY_GRADE_SECRET, 
        payload_json.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(transaction.digital_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Falha de integridade: Assinatura digital inválida."
        )
    
    # 2. Criptografia AES-256-GCM do payload
    encrypted_data = encrypt_payload(payload)
    
    # 3. Registro no Ledger Imutável
    previous_block = blockchain_ledger[-1]
    new_index = previous_block["index"] + 1
    
    new_block_data = {
        "index": new_index,
        "timestamp": time.time(),
        "payload": encrypted_data,  # Armazena o payload criptografado no ledger
        "previous_hash": previous_block["block_hash"]
    }
    
    new_block_data["block_hash"] = calculate_block_hash(new_block_data)
    blockchain_ledger.append(new_block_data)
    
    return {
        "status": "200 OK",
        "message": "Transação validada, criptografada com AES-256 e registrada com sucesso!",
        "block_index": new_index,
        "encrypted_envelope": encrypted_data,
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
