from fastapi import APIRouter, FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List
from datetime import date

app = FastAPI(title="S Message API")

# --- Configuração de Segurança ---
ADMIN_SECRET = "S@int#001"

def verify_admin(x_admin_token: str = Header(...)):
    if x_admin_token != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Acesso negado: Token inválido.")

# --- Router de Pagamentos ---
payments_router = APIRouter(prefix="/api/v1/payments", tags=["Payments & Wallet"])

class DepositRequest(BaseModel):
    amount: float
    signature: str

@payments_router.get("/wallet/{user_id}/statement")
async def get_wallet_statement(user_id: str):
    return {"user_id": user_id, "balance": 0.0, "transactions": []}

@payments_router.post("/wallet/{user_id}/deposit")
async def make_deposit(user_id: str, payload: DepositRequest):
    return {"status": "success", "user_id": user_id, "deposited_amount": payload.amount}

app.include_router(payments_router)

# --- Utilitário de Mapeamento Protegido ---
def map_app_routes(app: FastAPI):
    routes_info = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            for method in route.methods:
                routes_info.append({"method": method, "path": route.path})
    return routes_info

@app.get("/api/v1/system/routes", dependencies=[Depends(verify_admin)])
async def list_routes():
    return {"total_routes": len(app.routes), "routes": map_app_routes(app)}

# --- Router de BPO Financeiro ---
bpo_router = APIRouter(prefix="/api/v1/bpo", tags=["BPO Financeiro"])

class FinancialTransaction(BaseModel):
    description: str
    amount: float
    type: str
    due_date: date
    status: str = "pendente"

@bpo_router.get("/transactions", dependencies=[Depends(verify_admin)])
async def list_bpo_transactions():
    return {"status": "success", "managed_transactions": []}

@bpo_router.post("/transactions", dependencies=[Depends(verify_admin)])
async def create_bpo_transaction(transaction: FinancialTransaction):
    return {"message": "Transação registrada com sucesso", "data": transaction}

@bpo_router.get("/reports/closing/{client_id}", dependencies=[Depends(verify_admin)])
async def get_monthly_closing(client_id: str):
    return {"client_id": client_id, "status": "Em andamento"}

app.include_router(bpo_router)
