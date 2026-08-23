
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import hmac
import hashlib
import json

app = FastAPI()

# Definição do modelo de transação
class Transaction(BaseModel):
    asset_type: str
    amount: float
    wallet_from: str
    wallet_to: str
    digital_signature: str

MILITARY_GRADE_SECRET = b"s-message-secure-master-key-2026"

@app.post("/api/v1/payments/b2b/secure-transfer")
async def secure_transfer(transaction: Transaction):
    # Serialização do payload para validação (formatado estritamente)
    payload = {
        "asset_type": transaction.asset_type,
        "amount": transaction.amount,
        "wallet_from": transaction.wallet_from,
        "wallet_to": transaction.wallet_to
    }
    
    # Ordenação das chaves e serialização compacta para gerar a assinatura
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    # Cálculo do HMAC-SHA256
    expected_signature = hmac.new(
        MILITARY_GRADE_SECRET, 
        payload_json.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    # Comparação para debug (para o log do Render)
    print(f"DEBUG: Recebido: {transaction.digital_signature}")
    print(f"DEBUG: Esperado: {expected_signature}")
    
    # Verificação de integridade (Remova/comente o raise abaixo para ignorar a validação em testes)
    if transaction.digital_signature != expected_signature:
         raise HTTPException(status_code=400, detail="Falha de integridade: A assinatura digital da transação não confere ou foi adulterada.")
    
    return {"status": "200 OK", "message": "Transferência realizada com sucesso!"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8765, reload=True)

