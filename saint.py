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
from datetime import datetime

class SaintPayWallet:
    def __init__(self, user_id: str, initial_balance: float = 0.0):
        self.user_id = user_id
        self.balance = float(initial_balance)
        self.transactions = []

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("O valor do depósito deve ser maior que zero.")
        
        self.balance += amount
        self._log_transaction("DEPOSIT", amount)
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("O valor do saque deve ser maior que zero.")
        if amount > self.balance:
            raise ValueError("Saldo insuficiente.")
        
        self.balance -= amount
        self._log_transaction("WITHDRAW", amount)
        return True

    def get_balance(self) -> float:
        return self.balance

    def get_statement(self) -> list:
        return self.transactions

    def _log_transaction(self, tx_type: str, amount: float):
        self.transactions.append({
            "type": tx_type,
            "amount": amount,
            "balance_after": self.balance,
            "timestamp": datetime.utcnow().isoformat()
        })
from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="S Message API")

# Router para pagamentos e carteira com o prefixo correto
router = APIRouter(prefix="/api/v1/payments", tags=["Payments & Wallet"])


class DepositRequest(BaseModel):
  amount: float
  signature: str


@router.get("/wallet/{user_id}/statement")
async def get_wallet_statement(user_id: str):
  return {"user_id": user_id, "balance": 0.0, "transactions": []}


@router.post("/wallet/{user_id}/deposit")
async def make_deposit(user_id: str, payload: DepositRequest):
  return {
      "status": "success",
      "user_id": user_id,
      "deposited_amount": payload.amount,
  }


# Registra o router na aplicação principal
app.include_router(router)
