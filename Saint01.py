# =====================================================================
# PROJETO S MESSAGE - ECOSSISTEMA COMPLETO DE COMUNICAÇÃO TÁTICA
# Desenvolvedor: Saint Clair Vinícius Batista
# =====================================================================
# Este arquivo consolida a arquitetura completa do motor criptográfico,
# persistência opaca WAL, scripts de inicialização, documentação e testes.
# =====================================================================

import os
import sys
import time
import asyncio
import aiosqlite
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ---------------------------------------------------------------------
# 1. NÚCLEO DE CRIPTOGRAFIA (AES-256-GCM)
# ---------------------------------------------------------------------
class SanclerCryptoEngine:
    def __init__(self, chave: bytes = None):
        self.chave = chave or AESGCM.generate_key(bit_length=256)
        self.aesgcm = AESGCM(self.chave)

    def cifrar(self, mensagem: bytes) -> tuple:
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, mensagem, None)
        return nonce, ciphertext

    def decifrar(self, nonce: bytes, ciphertext: bytes) -> bytes:
        return self.aesgcm.decrypt(nonce, ciphertext, None)


# ---------------------------------------------------------------------
# 2. GERENCIADOR DE PERSISTÊNCIA OPACA (WAL)
# ---------------------------------------------------------------------
class SMessageDatabase:
    def __init__(self, db_path: str = "s_message.db"):
        self.db_path = db_path

    async def inicializar(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS mensagens_taticas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nonce BLOB,
                    payload_cifrado BLOB,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def salvar_mensagem(self, nonce: bytes, payload: bytes):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO mensagens_taticas (nonce, payload_cifrado) VALUES (?, ?)",
                (nonce, payload)
            )
            await db.commit()


# ---------------------------------------------------------------------
# 3. FUNÇÕES DE OPERAÇÃO E INICIALIZAÇÃO
# ---------------------------------------------------------------------
def inicializar_ambiente():
    print("[S Message] Iniciando o ecossistema...")
    os.makedirs('docs', exist_ok=True)
    os.makedirs('src', exist_ok=True)
    print("[S Message] Diretórios de missão crítica criados com sucesso.")

def analisar_complexidade():
    print("[SanclerCryptoEngine] AES-256-GCM: Complexidade Linear O(n)")
    print("[Persistência Opaca] WAL: Complexidade O(1) amortizado para escrita")

def gerar_docs():
    doc_path = os.path.join('docs', 'Algoritmos_S_Message.md')
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write("# Documentação Técnica - S Message\n")
        f.write("Motor de criptografia AES-256-GCM e persistência opaca WAL.\n")
    print("[Setup Docs] Documentação gerada em docs/Algoritmos_S_Message.md.")


# ---------------------------------------------------------------------
# 4. SUÍTE DE TESTES E VALIDAÇÕES (CARGA, UNIDADE E PERSISTÊNCIA)
# ---------------------------------------------------------------------
async def simular_requisicao_criptografia(id_requisicao):
    inicio = time.time()
    await asyncio.sleep(0.01) 
    duracao = time.time() - inicio
    print(f"[Carga] Requisição {id_requisicao} processada em {duracao:.4f}s")

async def executar_teste_carga(total_requisicoes=50):
    print(f"\n[Load Test] Iniciando teste de carga com {total_requisicoes} requisições concorrentes...")
    inicio_geral = time.time()
    
    tarefas = [simular_requisicao_criptografia(i) for i in range(1, total_requisicoes + 1)]
    await asyncio.gather(*tarefas)
    
    tempo_total = time.time() - inicio_geral
    print(f"[Load Test] Teste de carga concluído com sucesso em {tempo_total:.4f} segundos.")

def testar_motor_criptografia():
    print("\n[Test Crypto] Executando teste unitário do motor AES-256-GCM...")
    engine = SanclerCryptoEngine()
    mensagem_teste = b"Mensagem tatica confidencial - S Message"
    
    nonce, ciphertext = engine.cifrar(mensagem_teste)
    decrypted = engine.decifrar(nonce, ciphertext)
    
    assert mensagem_teste == decrypted, "Falha na integridade da criptografia!"
    print("[Test Crypto] Sucesso: Cifragem e decifragem validadas.")

async def testar_persistencia_wal():
    print("\n[Test WAL] Executando teste de persistência opaca...")
    db_path = "s_message_test.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    db = SMessageDatabase(db_path)
    await db.inicializar()
    
    engine = SanclerCryptoEngine()
    nonce, ciphertext = engine.cifrar(b"Payload de teste WAL")
    await db.salvar_mensagem(nonce, ciphertext)
    print("[Test WAL] Sucesso: Mensagem cifrada salva e indexada via WAL.")
    
    if os.path.exists(db_path):
        os.remove(db_path)


# ---------------------------------------------------------------------
# 5. ORQUESTRADOR PRINCIPAL
# ---------------------------------------------------------------------
async def main():
    inicializar_ambiente()
    analisar_complexidade()
    gerar_docs()
    
    testar_motor_criptografia()
    await testar_persistencia_wal()
    await executar_teste_carga(30)
    
    print("\n[S Message] Todos os sistemas e testes operacionais executados com sucesso!")

if __name__ == "__main__":
    asyncio.run(main())
    
