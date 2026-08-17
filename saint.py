# [Mantenha seus imports no topo]

# [Mantenha suas classes existentes: Transaction, SecureMessage]

class DropshippingOrder(BaseModel):
    supplier_id: str
    client_destination: str
    sku_code: str
    quantity: int
    unit_price_usd: float
    digital_signature: str

# [Mantenha suas rotas existentes: /payments/b2b/secure-transfer, /messages/send, /messages/sign]

@app.post("/api/v1/dropshipping/dispatch")
async def dispatch_supplier_order(order: DropshippingOrder):
    # Lógica de validação com a mesma chave secreta
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
