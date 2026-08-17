from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hmac
import hashlib
import json

app = FastAPI()

# Chave secreta de blindagem DEFCON 1
MILITARY_GRADE_SECRET = b"s-message-secure-master-key-2026"

# Modelos de Dados
class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float
    digital_signature: str

class SecureMessage(BaseModel):
    sender: str
    recipient: str
    content: str
    digital_signature: str

class DropshippingOrder(BaseModel):
    supplier_id: str
    client_destination: str
    sku_code: str
    quantity: int
    unit_price_usd: float
    digital_signature: str

# Rotas do Sistema S Message
@app.post("/api/v1/messages/send")
async def send_message(message: SecureMessage):
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
        raise HTTPException(
            status_code=400, 
            detail="DEFCON 1: Assinatura inválida! Violação de integridade detectada na mensagem."
        )
        
    return {
        "status": "200 OK",
        "defcon_level": "DEFCON 1",
        "delivery": "Mensagem entregue com segurança criptográfica absoluta."
    }

@app.post("/api/v1/payments/b2b/secure-transfer")
async def secure_transfer(tx: Transaction):
    payload = {
        "amount": tx.amount,
        "recipient": tx.recipient,
        "sender": tx.sender
    }
    
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    expected_signature = hmac.new(
        MILITARY_GRADE_SECRET, 
        payload_json.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    if tx.digital_signature != expected_signature:
        raise HTTPException(
            status_code=400, 
            detail="DEFCON 1: Falha crítica! Transferência rejeitada por adulteração de payload."
        )
        
    return {
        "status": "200 OK",
        "defcon_level": "DEFCON 1",
        "transaction_status": "Transferência B2B validada e processada com sucesso."
    }

@app.post("/api/v1/dropshipping/dispatch")
async def dispatch_supplier_order(order: DropshippingOrder):
    payload = {
        "client_destination": order.client_destination,
        "quantity": order.quantity,
        "sku_code": order.sku_code,
        "supplier_id": order.supplier_id,
        "unit_price_usd": order.unit_price_usd
    }
    
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    expected_signature = hmac.new(
        MILITARY_GRADE_SECRET, 
        payload_json.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    if order.digital_signature != expected_signature:
         raise HTTPException(
             status_code=400, 
             detail="DEFCON 1: Falha crítica de integridade na ordem de fornecimento internacional!"
         )
    
    return {
        "status": "200 OK",
        "defcon_level": "DEFCON 1",
        "dispatch_status": "Ordem despachada com segurança máxima para o fornecedor na China."
    }
