from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import os
import time
from datetime import datetime

app = FastAPI()

# ─── DADOS DO CANAL / SERVIDOR ───
NOME_CANAL = "Seu Canal"
STATUS_TRANSMISSAO = False
ESPECTADORES = {}

COMANDOS = {
    "!ajuda": "Lista de comandos disponíveis: !ajuda, !regras, !horario, !status",
    "!regras": "📜 Regras: Respeito, educação, proibido spam e links inadequados.",
    "!horario": "🕒 Transmissões: Terça a Sábado, a partir das 19h.",
    "!status": None  # Dinâmico
}

MENSAGENS_BOAS_VINDAS = [
    "Bem-vindo(a)! Aproveite a transmissão! 🎉",
    "Olá! Fique à vontade e participe! 💬",
    "Bem-vindo(a)! É ótimo te ver aqui! ✨"
]

# ─── ROTAS PRINCIPAIS ───
@app.get("/", response_class=HTMLResponse)
async def pagina_inicial():
    status_cor = "🟢 ONLINE" if STATUS_TRANSMISSAO else "🔴 OFFLINE"
    return f"""
    <html>
    <body style="background:#f0f0f0; font-family:sans-serif; text-align:center; padding-top:80px;">
        <h1 style="color:green; font-size:32px;">✅ ONLINE / ARMADO</h1>
        <h2>Canal: {NOME_CANAL}</h2>
        <p style="font-size:22px;">Status: {status_cor}</p>
        <p>Espectadores conectados: {len(ESPECTADORES)}</p>
        <p style="margin-top:40px; color:#666;">Servidor ativo e funcionando corretamente.</p>
    </body>
    </html>
    """

@app.get("/status", response_class=JSONResponse)
async def status_servidor():
    return {
        "canal": NOME_CANAL,
        "status": "online" if STATUS_TRANSMISSAO else "offline",
        "espectadores": len(ESPECTADORES),
        "horario_atual": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

@app.get("/comandos", response_class=JSONResponse)
async def listar_comandos():
    return {"comandos": list(COMANDOS.keys())}

# ─── INICIALIZAÇÃO — PORTA DINÂMICA ───
if __name__ == "__main__":
    import uvicorn
    # Render define a porta automaticamente; local usa 8000
    porta = int(os.getenv("PORT", 8000))
    print(f"🚀 Iniciando servidor...")
    print(f"📍 Modo local: http://127.0.0.1:{porta}")
    print(f"🌐 Render: URL do serviço (sem porta no final)")
    uvicorn.run("main:app", host="0.0.0.0", port=porta)
