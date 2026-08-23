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
