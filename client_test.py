import asyncio
import httpx
import websockets
import json

# Substitua pela URL pública exata do seu serviço Saint01 no Render
BASE_URL = "https://saint01.onrender.com"
WS_URL = "wss://saint01.onrender.com/ws/soc"

# Credenciais oficiais e assinaturas válidas
VALID_TOKEN = "admin_token_2026"
VALID_LICENSE = "LIC-SANTI-2026-X99"
VALID_APP_SIG = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

async def listen_soc():
    """Ouve os eventos de segurança do SOC em tempo real via WebSocket na nuvem"""
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("🛡️ [SOC WebSocket] Conectado ao canal de auditoria em tempo real na nuvem.")
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"📡 [SOC Evento]: {data.get('type')} -> Endpoint: {data['data'].get('endpoint')} | Status: {data['data'].get('status')}")
    except websockets.exceptions.ConnectionClosed:
        print("🛡️ [SOC WebSocket] Conexão encerrada.")
    except Exception as e:
        print(f"🛡️ [SOC WebSocket] Erro: {e}")

async def run_cloud_tests():
    print("☁️ [INÍCIO DOS TESTES NA NUVEM - SAINT01]\n")
    
    soc_task = asyncio.create_task(listen_soc())
    await asyncio.sleep(1.5) # Aguarda estabilizar a conexão WS

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15.0) as client:
        
        # ---------------------------------------------------------
        # TESTE 1: Requisição Válida na Nuvem (Perfil 8.2ms)
        # ---------------------------------------------------------
        print("\n--- Teste 1 (Nuvem): Fluxo Autenticado e Licenciado ---")
        headers_ok = {
            "Authorization": f"Bearer {VALID_TOKEN}",
            "X-Client-License": VALID_LICENSE,
            "X-App-Signature": VALID_APP_SIG,
            "X-Request-ID": "cloud-req-001"
        }
        
        try:
            response = await client.post("/api/v1/chat", headers=headers_ok, json={"prompt": "Olá da nuvem, Santi!"})
            print(f"Status HTTP: {response.status_code}")
            print(f"Resposta: {response.json()}")
        except Exception as e:
            print(f"Erro no Teste 1: {e}")

        await asyncio.sleep(1)

        # ---------------------------------------------------------
        # TESTE 2: Violação de Fingerprint na Nuvem (Air-Gap)
        # ---------------------------------------------------------
        print("\n--- Teste 2 (Nuvem): Violação de Fingerprint (Air-Gap) ---")
        headers_hack = {
            "Authorization": f"Bearer {VALID_TOKEN}",
            "X-Client-License": VALID_LICENSE,
            "X-App-Signature": "assinatura_falsa_tentativa_intrusao",
            "X-Request-ID": "cloud-req-002"
        }
        
        try:
            response = await client.post("/api/v1/chat", headers=headers_hack, json={"prompt": "Ataque"})
            print(f"Status HTTP: {response.status_code}")
            print(f"Resposta: {response.json()}")
        except Exception as e:
            print(f"Erro no Teste 2: {e}")

    await asyncio.sleep(1)
    soc_task.cancel()
    print("\n🏁 [FIM DOS TESTES NA NUVEM]")

if __name__ == "__main__":
    asyncio.run(run_cloud_tests())
