import requests

def executar_cliente_transferencia():
    url = "http://127.0.0.1:10000/api/v1/secure-transfer-biometric"
    
    # Dados da transação comercial
    payload = {
        "asset_code": "BRL_DIGITAL",
        "amount": "50.0",
        "wallet_from": "carteira_santi_123",
        "wallet_to": "carteira_destino_456",
        "digital_signature": "SUA_ASSINATURA_HMAC_AQUI"
    }
    
    # Caminho da foto para biometria (ajustado para o Android/Pydroid se necessário)
    foto_path = "/storage/emulated/0/Pictures/Screenshots/foto1.png"
    
    try:
        with open(foto_path, "rb") as f:
            files = {"face_image": ("foto1.png", f, "image/png")}
            
            print("[+] Enviando requisição para a API S Message...")
            response = requests.post(url, data=payload, files=files)
            
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {response.json()}")
        
    except FileNotFoundError:
        print(f"[-] Erro: Arquivo de imagem não encontrado em {foto_path}")
    except Exception as e:
        print(f"[-] Erro na requisição: {e}")

if __name__ == "__main__":
    executar_cliente_transferencia()
import hmac
import hashlib
import time
import requests

# Configurações da transação
URL_API = "http://127.0.0.1:10000/api/v1/secure-transfer-biometric"
SECRET_KEY = b"sua_chave_secreta_compartilhada"  # Deve bater com a chave do servidor

WALLET_FROM = "carteira_santi_123"
WALLET_TO = "carteira_destino_456"
ASSET_CODE = "BRL_DIGITAL"
AMOUNT = "50.0"
FOTO_PATH = "/storage/emulated/0/Pictures/Screenshots/foto1.png"

def gerar_assinatura_hmac(wallet_from: str, wallet_to: str, amount: str) -> str:
    # Mensagem padronizada para assinar a transação
    mensagem = f"{wallet_from}:{wallet_to}:{amount}"
    assinatura = hmac.new(SECRET_KEY, mensagem.encode("utf-8"), hashlib.sha256).hexdigest()
    return assinatura

def executar_cliente():
    print("[*] Gerando assinatura HMAC...")
    digital_signature = gerar_assinatura_hmac(WALLET_FROM, WALLET_TO, AMOUNT)
    
    payload = {
        "asset_code": ASSET_CODE,
        "amount": AMOUNT,
        "wallet_from": WALLET_FROM,
        "wallet_to": WALLET_TO,
        "digital_signature": digital_signature
    }
    
    try:
        print(f"[*] Lendo imagem biométrica em: {FOTO_PATH}")
        with open(FOTO_PATH, "rb") as f:
            files = {"face_image": ("foto1.png", f, "image/png")}
            
            print("[+] Disparando requisição para o S Message...")
            response = requests.post(URL_API, data=payload, files=files)
            
        print(f"\n[HTTP Status] {response.status_code}")
        print(f"[Resposta] {response.json()}")
        
    except FileNotFoundError:
        print(f"[-] Erro: Arquivo de imagem não encontrado no caminho {FOTO_PATH}.")
    except requests.exceptions.ConnectionError:
        print("[-] Erro: Não foi possível conectar ao servidor. Verifique se o backend está rodando na porta 10000.")
    except Exception as e:
        print(f"[-] Erro inesperado: {e}")

if __name__ == "__main__":
    executar_cliente()
