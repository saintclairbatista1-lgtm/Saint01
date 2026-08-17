from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import hmac
import hashlib
import json

app = FastAPI()

# Definição do modelo de transação financeira
class Transaction(BaseModel):
    asset_type: str
    amount: float
    wallet_from: str
    wallet_to: str
    digital_signature: str

# Definição do modelo para o S Message
class SecureMessage(BaseModel):
    sender: str
    recipient: str
    content: str
    digital_signature: str

MILITARY_GRADE_SECRET = b"s-message-secure-master-key-2026"

@app.post("/api/v1/payments/b2b/secure-transfer")
async def secure_transfer(transaction: Transaction):
    payload = {
        "asset_type": transaction.asset_type,
        "amount": transaction.amount,
        "wallet_from": transaction.wallet_from,
        "wallet_to": transaction.wallet_to
    }
    
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    expected_signature = hmac.new(
        MILITARY_GRADE_SECRET, 
        payload_json.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    if transaction.digital_signature != expected_signature:
         raise HTTPException(status_code=400, detail="Falha de integridade: A assinatura digital da transação não confere ou foi adulterada.")
    
    return {"status": "200 OK", "message": "Transferência realizada com sucesso!"}

@app.post("/api/v1/messages/send")
async def send_secure_message(message: SecureMessage):
    # Serialização estrita para validar a integridade da mensagem
    payload = {
        "content": message.content,
        "recipient": message.recipient,
        "sender": message.sender
    }
    
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    expected_signature = hmac.new(
        MILITARY_GRADE_SECRET, 
        payload_json.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    if message.digital_signature != expected_signature:
         raise HTTPException(status_code=400, detail="Falha de integridade: A assinatura digital da mensagem não confere ou foi adulterada.")
    
    return {"status": "200 OK", "delivery": "Mensagem criptografada entregue com segurança no S Message!"}
    @app.post("/api/v1/messages/sign")
async def sign_message(message: SecureMessage):
    payload = {
        "content": message.content,
        "recipient": message.recipient,
        "sender": message.sender
    }
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    expected_signature = hmac.new(
        MILITARY_GRADE_SECRET, 
        payload_json.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    return {"signature": expected_signature}

