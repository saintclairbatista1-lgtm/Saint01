import hmac
import hashlib
import json
import requests

# Substitua pelo seu domínio real do Render (ex: https://saint01.onrender.com)
BASE_URL = "https://SEU-DOMINIO-REAL.onrender.com"
MILITARY_GRADE_SECRET = b"s-message-secure-master-key-2026"

# Dados da operação
payload = {
    "amount": 100.0,
    "user_id": "santi_01"
}

# Serialização estrita exigida pela API (ordenada e sem espaços extras)
payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))

# Geração da assinatura HMAC-SHA256
digital_signature = hmac.new(
    MILITARY_GRADE_SECRET, 
    payload_json.encode('utf-8'), 
    hashlib.sha256
).hexdigest()

# Montagem do corpo final da requisição
body = {
    "user_id": payload["user_id"],
    "amount": payload["amount"],
    "digital_signature": digital_signature
}

print("Payload JSON:", payload_json)
print("Assinatura gerada:", digital_signature)

# Disparando o POST para o Render
response = requests.post(f"{BASE_URL}/api/v1/wallet/deposit", json=body)
print("Status Code:", response.status_code)
print("Resposta da API:", response.json())
