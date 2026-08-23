import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def testar_criptografia_500bytes():
    print("[*] Iniciando teste do microprocessador virtual de 500 bytes...")

    # 1. Simula a inicialização do buffer mestre (como no main.py do S Message)
    input_bytes = b"s-message-secure-master-buffer-500-bytes-2026"
    padded_buffer = bytearray()
    seed = input_bytes
    
    while len(padded_buffer) < 500:
        seed = hashlib.sha512(seed).digest()
        padded_buffer.extend(seed)

    master_register = bytes(padded_buffer[:500])
    print(f"[OK] Buffer mestre gerado com sucesso. Tamanho: {len(master_register)} bytes.")

    # 2. Extrai a chave AES de 32 bytes do registrador
    aes_key_segment = master_register[:32]
    aesgcm = AESGCM(aes_key_segment)

    # 3. Prepara os dados de teste (plaintext e nonce de 12 bytes)
    nonce = b"\x01" * 12
    plaintext = b"S Message - Teste de Criptografia AES-GCM bem-sucedido!"

    # 4. Executa a criptografia
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    print(f"[OK] Criptografia AES-GCM executada com sucesso!")
    print(f" -> Ciphertext (Hex): {ciphertext.hex()}")

    # 5. Executa a descriptografia para validar a integridade
    decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
    decrypted_text = decrypted_bytes.decode('utf-8')
    print(f"[OK] Descriptografia validada com sucesso!")
    print(f" -> Texto recuperado: {decrypted_text}")

    if decrypted_text == plaintext.decode('utf-8'):
        print("\n[SUCESSO ABSOLUTO] O subsistema criptográfico está 100% operacional!")
    else:
        print("\n[FALHA] Os dados descriptografados não coincidem.")

if __name__ == "__main__":
    testar_criptografia_500bytes()
