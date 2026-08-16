from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "S Message API funcionando com sucesso!"}
from functools import wraps

# Decorador para proteger rotas com JWT e segredo dinâmico
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # O token geralmente vem no cabeçalho Authorization: Bearer <token>
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token malformado!'}), 401
                
        if not token:
            return jsonify({'message': 'Token de acesso ausente!'}), 401
            
        try:
            secret = get_current_secret()
            # Valida o token usando o segredo atual (ou o histórico de rotação)
            data = jwt.decode(token, secret, algorithms=["HS256"])
            current_user = data['user']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado! Faça refresh ou login novamente.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

# Exemplo de rota protegida no S Message
@app.route('/messages', methods=['GET'])
@token_required
def get_messages(current_user):
    # Apenas usuários autenticados com token válido chegam aqui
    return jsonify({
        'user': current_user,
        'messages': [] # Aqui entraria a listagem real de mensagens
    })
