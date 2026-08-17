from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI(
    title="S Message API",
    description="Backend de alta segurança e transações B2B para o ecossistema S Message",
    version="1.0.0"
)

# Mapeamento dos endereços de contrato dos ativos digitais suportados
TOKEN_MAP: Dict[str, str] = {
    "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
    "EURO_DIGITAL": "0x_euro_digital_placeholder",
    "BREX": "0x_brex_placeholder"
}

# Modelo de dados para requisições de pagamento B2B
class PaymentRequest(BaseModel):
    asset_type: str  # Ex: "USDC", "USDT", "BREX", "EURO_DIGITAL"
    amount: float
    wallet_from: str
    wallet_to: str

@app.get("/")
async def root():
    return {
        "status": "online",
        "system": "S Message API",
        "security": "AES-256-GCM / mTLS Ready"
    }

@app.post("/api/v1/payments/b2b/transfer")
async def process_transfer(request: PaymentRequest):
    # Validação do ativo solicitado
    asset_upper = request.asset_type.upper()
    if asset_upper not in TOKEN_MAP:
        raise HTTPException(
            status_code=400, 
            detail=f"Ativo '{request.asset_type}' não suportado pelo sistema."
        )
    
    token_address = TOKEN_MAP[asset_upper]
    
    # Retorno estruturado para a transação B2B
    return {
        "status": "processing",
        "asset": asset_upper,
        "amount": request.amount,
        "contract_address": token_address,
        "sender": request.wallet_from,
        "recipient": request.wallet_to,
        "message": f"Transação B2B de {request.amount} {asset_upper} validada para processamento."
    }
