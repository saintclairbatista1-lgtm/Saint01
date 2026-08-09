# Saint clair vinicius chat
import threading
import socket

def iniciar_chat():
    print("=== APP DE MENSAGENS Saint clair vinicius===")
    modo = input("Digite 's' para Servidor ou 'c' para Cliente: ").lower()
    
    host = '127.0.0.1'
    porta = 5000
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if modo == 's':
        s.bind((host, porta))
        s.listen(1)
        print("Aguardando conexão...")
        conn, addr = s.accept()
        print(f"Conectado com: {addr}")
        
        # Thread para receber mensagens
        threading.Thread(target=receber, args=(conn,), daemon=True).start()
        enviar(conn)
    else:
        try:
            s.connect((host, porta))
            print("Conectado ao servidor!")
            
            # Thread para receber mensagens
            threading.Thread(target=receber, args=(s,), daemon=True).start()
            enviar(s)
        except:
            print("Não foi possível conectar. O servidor está ligado?")

def receber(conexao):
    while True:
        try:
            mensagem = conexao.recv(1024).decode('utf-8')
            if not mensagem:
                break
            print(f"\nOutra pessoa: {mensagem}")
        except:
            break

def enviar(conexao):
    while True:
        msg = input("Você: ")
        if msg.lower() == 'sair':
            conexao.close()
            break
        conexao.send(msg.encode('utf-8'))

if __name__ == "__main__":
    iniciar_chat()
