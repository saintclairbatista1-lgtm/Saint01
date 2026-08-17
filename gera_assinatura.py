import hmac
import hashlib
import json

# Chave secreta e dados da transação idênticos aos configurados no seu saint.py
SECRET_KEY = b"sua-chave-secreta-militar"  # Substitua pela chave real do seu backend
payload = {
    "asset_type": "USDC",
    "amount": 1500.50,
    "wallet_from": "0xSenderWallet123",
    "wallet_to": "0xRecipientWallet456"
}

# Serializa o payload exatamente como o FastAPI recebe
payload_str = json.dumps(payload, separators=(',', ':'))

# Calcula o HMAC-SHA256
signature = hmac.new(SECRET_KEY, payload_str.encode('utf-8'), hashlib.sha256).hexdigest()
print("Assinatura HMAC Válida:", signature)

