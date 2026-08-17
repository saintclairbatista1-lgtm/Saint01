
from functools import wraps
from fastapi import FastAPI, HTTPException, Request, Header
from typing import Optional

# Inicialização do aplicativo FastAPI
app = FastAPI(
    title="S Message API",
    description="API do aplicativo S Message",
    version="1.0.0"
)

# Decorador para verificação/proteção por Token
def token_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        # A lógica de extração e validação do token fica aqui
        token = kwargs.get("authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Token de acesso ausente ou inválido")
        return await f(*args, **kwargs)
    return decorated

# Rota principal (Health Check)
@app.get("/")
def read_root():
    return {"message": "S Message API está rodando com sucesso!"}

# Exemplo de rota protegida usando FastAPI
@app.get("/protected")
def protected_route(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Não autorizado")
    return {"status": "Acesso concedido", "user_data": "Dados protegidos"}
