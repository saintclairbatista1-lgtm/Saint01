from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hmac
import hashlib
import json
import time

app = FastAPI(
    title="Saint01 - S Message Secure Ledger",
    version="2.0.0",
    description="API de Transferência B2B com Validação HMAC e Auditoria em Ledger Imutável"
)

# Definição do modelo de transação
class Transaction(BaseModel):
    asset_type: str
    amount: float
    wallet_from: str
    wallet_to: str
    digital_signature: str

MILITARY_GRADE_SECRET = b"s-message-secure-master-key-2026"

# Estrutura inicial do Ledger (Gênesis)
blockchain_ledger = [{
    "index": 0,
    "timestamp": 0.0,
    "payload": "Genesis Block",
    "previous_hash": "0" * 64,
    "block_hash": "0" * 64
}]

def calculate_block_hash(block: dict) -> str:
    block_string = json.dumps({
        "index": block["index"],
        "timestamp": block["timestamp"],
        "payload": block["payload"],
        "previous_hash": block["previous_hash"]
    }, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

@app.post("/api/v1/payments/b2b/secure-transfer")
async def secure_transfer(transaction: Transaction):
    # 1. Serialização estrita do payload para o HMAC (mesma ordem usada pelo cliente)
    payload = {
        "asset_type": transaction.asset_type,
        "amount": transaction.amount,
        "wallet_from": transaction.wallet_from,
        "wallet_to": transaction.wallet_to
    }
    
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    # 2. Cálculo e validação do HMAC-SHA256
    expected_signature = hmac.new(
        MILITARY_GRADE_SECRET, 
        payload_json.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    # Logs para depuração no ambiente de nuvem (Render/Koyeb)
    print(f"DEBUG - Recebido: {transaction.digital_signature}")
    print(f"DEBUG - Esperado: {expected_signature}")
    
    if transaction.digital_signature != expected_signature:
        raise HTTPException(
            status_code=400, 
            detail="Falha de integridade: A assinatura digital da transação não confere ou foi adulterada."
        )
    
    # 3. Construção do Novo Bloco no Ledger de Auditoria Imutável
    previous_block = blockchain_ledger[-1]
    new_index = previous_block["index"] + 1
    timestamp = time.time()
    
    new_block_data = {
        "index": new_index,
        "timestamp": timestamp,
        "payload": payload,
        "previous_hash": previous_block["block_hash"]
    }
    
    # Gera o hash criptográfico definitivo do bloco atual
    new_block_data["block_hash"] = calculate_block_hash(new_block_data)
    
    # Adiciona à cadeia
    blockchain_ledger.append(new_block_data)
    
    return {
        "status": "200 OK", 
        "message": "Transferência validada e registrada no Ledger imutável!",
        "block_index": new_index,
        "block_hash": new_block_data["block_hash"]
    }

@app.get("/api/v1/audit/chain")
async def get_audit_chain():
    return {
        "chain_length": len(blockchain_ledger),
        "ledger": blockchain_ledger
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8765, reload=True)
