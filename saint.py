from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import hmac
import hashlib
import json
import time

# Inicialização da aplicação FastAPI para o S Message
app = FastAPI(
    title="Saint01 - S Message Secure Ledger",
    version="2.0.1",
    description="API de Transferência B2B com Validação HMAC e Auditoria em Ledger Imutável"
)

# Definição do modelo de transação utilizando Pydantic para validação estrita de dados
class Transaction(BaseModel):
    asset_type: str = Field(..., description="Tipo de ativo sendo transferido")
    amount: float = Field(..., gt=0, description="Valor da transação (deve ser maior que zero)")
    wallet_from: str = Field(..., description="Identificador da carteira de origem")
    wallet_to: str = Field(..., description="Identificador da carteira de destino")
    digital_signature: str = Field(..., description="Assinatura HMAC-SHA256 gerada pelo cliente")

# Chave secreta de nível militar para validação de assinaturas digitais
MILITARY_GRADE_SECRET = b"s-message-secure-master-key-2026"

# Estrutura inicial do Ledger (Bloco Gênesis) para auditoria imutável
blockchain_ledger = [{
    "index": 0,
    "timestamp": 0.0,
    "payload": "Genesis Block",
    "previous_hash": "0" * 64,
    "block_hash": "0" * 64
}]

def calculate_block_hash(block: dict) -> str:
    """
    Função auxiliar para calcular o hash SHA-256 de um bloco.
    Utiliza ordenação de chaves (sort_keys=True) e separadores compactos 
    para garantir consistência matemática exata entre cliente e servidor.
    """
    block_string = json.dumps({
        "index": block["index"],
        "timestamp": block["timestamp"],
        "payload": block["payload"],
        "previous_hash": block["previous_hash"]
    }, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

@app.get("/", summary="Status do Servidor")
async def root():
    """Rota raiz para verificar se o servidor está online no GitHub/Cloud."""
    return {
        "status": "online",
        "project": "S Message Secure Ledger",
        "version": "2.0.1"
    }

@app.post("/api/v1/payments/b2b/secure-transfer", summary="Transferência B2B Segura")
async def secure_transfer(transaction: Transaction):
    """
    Endpoint responsável por receber transações B2B, validar a assinatura HMAC-SHA256
    e registar a operação num Ledger imutável de forma atômica e segura.
    """
    # 1. Serialização estrita do payload para o HMAC (mesma ordem usada pelo cliente)
    payload = {
        "asset_type": transaction.asset_type,
        "amount": transaction.amount,
        "wallet_from": transaction.wallet_from,
        "wallet_to": transaction.wallet_to
    }
    
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    
    # 2. Cálculo e validação do HMAC-SHA256 usando comparação segura contra timing attacks
    expected_signature = hmac.new(
        MILITARY_GRADE_SECRET, 
        payload_json.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    # Validação de integridade da assinatura digital
    if not hmac.compare_digest(transaction.digital_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Falha de integridade: A assinatura digital da transação não confere ou foi adulterada."
        )
    
    # 3. Construção do Novo Bloco no Ledger de Auditoria Imutável
    previous_block = blockchain_ledger[-1]
    new_index = previous_block["index"] + 1
    timestamp = time.time()
    
    new_block_data = {
        "index": new_index,
        "timestamp": timestamp,
        "payload": payload,
        "previous_hash": previous_block["block_hash"]
    }
    
    # Gera o hash criptográfico definitivo do bloco atual
    new_block_data["block_hash"] = calculate_block_hash(new_block_data)
    
    # Adiciona o novo bloco à cadeia
    blockchain_ledger.append(new_block_data)
    
    return {
        "status": "200 OK", 
        "message": "Transferência validada e registrada no Ledger imutável com sucesso!",
        "block_index": new_index,
        "block_hash": new_block_data["block_hash"]
    }

@app.get("/api/v1/audit/chain", summary="Consultar Ledger de Auditoria")
async def get_audit_chain():
    """Retorna a cadeia completa do Ledger para efeitos de auditoria e transparência."""
    return {
        "chain_length": len(blockchain_ledger),
        "ledger": blockchain_ledger
    }

@app.get("/api/v1/audit/verify", summary="Verificar Integridade do Ledger")
async def verify_ledger_integrity():
    """
    Percorre todo o ledger desde o bloco Gênesis para validar matematicamente 
    se os hashes criptográficos e os encadeamentos estão intactos e inviolados.
    """
    for i in range(1, len(blockchain_ledger)):
        current_block = blockchain_ledger[i]
        previous_block = blockchain_ledger[i - 1]
        
        # 1. Verifica se o previous_hash aponta corretamente para o hash do bloco anterior
        if current_block["previous_hash"] != previous_block["block_hash"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quebra de cadeia detectada no bloco {current_block['index']}! O hash anterior não confere."
            )
            
        # 2. Recalcula o hash do bloco atual para garantir que o payload não foi alterado
        recalculated_hash = calculate_block_hash(current_block)
        if recalculated_hash != current_block["block_hash"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Adulteração de dados detectada no bloco {current_block['index']}! O hash recalculado difere."
            )

    return {
        "status": "200 OK",
        "message": "Ledger íntegra e verificada com sucesso! Nenhum sinal de adulteração.",
        "total_blocks_verified": len(blockchain_ledger)
    }

# Ponto de entrada para execução local do servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("site:app", host="127.0.0.1", port=8765, reload=True)
import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 1. Geração de uma chave mestra segura de 32 bytes (256 bits) para o AES
# Nota: Em produção, armazene esta chave de forma segura em variáveis de ambiente.
AES_MASTER_KEY = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(AES_MASTER_KEY)

def encrypt_data(data_dict: dict) -> dict:
    """
    Criptografa um dicionário/payload utilizando AES-256-GCM.
    Retorna o texto cifrado e o Nonce (IV) em formato hexadecimal.
    """
    # Gera um Nonce aleatório de 12 bytes (96 bits) recomendado para o modo GCM
    nonce = os.urandom(12)
    
    # Serializa o dicionário para bytes em formato JSON consistente
    message_bytes = json.dumps(data_dict, sort_keys=True).encode('utf-8')
    
    # Realiza a criptografia autenticada
    ciphertext = aesgcm.encrypt(nonce, message_bytes, None)
    
    return {
        "ciphertext_hex": ciphertext.hex(),
        "nonce_hex": nonce.hex()
    }

def decrypt_data(ciphertext_hex: str, nonce_hex: str) -> dict:
    """
    Descriptografa dados protegidos por AES-256-GCM a partir de strings hexadecimais.
    Valida automaticamente a integridade do conteúdo.
    """
    try:
        nonce = bytes.fromhex(nonce_hex)
        ciphertext = bytes.fromhex(ciphertext_hex)
        
        # Realiza a descriptografia e validação de autenticidade
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        
        # Converte os bytes de volta para dicionário Python
        return json.loads(decrypted_bytes.decode('utf-8'))
    except Exception as e:
        raise ValueError(f"Falha na descriptografia AES-GCM: Dados corrompidos ou chave inválida. Erro: {str(e)}")

# ==========================================
# Exemplo prático de uso local (Teste rápido)
# ==========================================
if __name__ == "__main__":
    # Dados de exemplo que você deseja proteger
    payload_original = {
        "wallet_from": "saint-wallet-01",
        "wallet_to": "target-wallet-09",
        "amount": 1500.50
    }
    
    # 1. Encriptando
    dados_cifrados = encrypt_data(payload_original)
    print("--- DADOS CIFRADOS (AES-256-GCM) ---")
    print(dados_cifrados)
    
    # 2. Decriptando
    payload_recuperado = decrypt_data(dados_cifrados["ciphertext_hex"], dados_cifrados["nonce_hex"])
    print("\n--- DADOS RECUPERADOS ---")
    print(payload_recuperado)
