import jwt
from flask import request, jsonify, current_app
from functools import wraps

def token_required(f):
    """
    Decorator para proteger rotas com autenticação JWT.
    Adiciona `request.user_id` e `request.user_type` com base no token.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token ausente!'}), 401

        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )
            request.user_id = data['user_id']
            request.user_type = data['user_type']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401

        return f(*args, **kwargs)

    return decorated
