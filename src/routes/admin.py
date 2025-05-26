from flask import Blueprint, request, jsonify, current_app # Added current_app
from src.models.user import db
from src.models.category import Category
from functools import wraps
import jwt
# import os # os is no longer needed for SECRET_KEY here

admin_bp = Blueprint('admin', __name__)

# Middleware para verificar se o usuário é administrador
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Token inválido'}), 401

        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401

        try:
            # Use the app's configured SECRET_KEY for consistency
            secret_key = current_app.config['SECRET_KEY'] 
            data = jwt.decode(token, secret_key, algorithms=["HS256"])
            if data['user_type'] != 'admin':
                return jsonify({'error': 'Acesso restrito a administradores'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        except Exception: # Catching a broader exception here just in case
            return jsonify({'error': 'Erro na validação do token'}), 401

        return f(*args, **kwargs)
    return decorated

# Rotas para gerenciamento de profissionais
@admin_bp.route('/professionals/pending', methods=['GET'])
@admin_required
def get_pending_professionals():
    # Implementação para listar profissionais pendentes
    return jsonify([])

@admin_bp.route('/professionals/<int:prof_id>/approve', methods=['POST'])
@admin_required
def approve_professional(prof_id):
    # Implementação para aprovar profissional
    return jsonify({'message': 'Profissional aprovado com sucesso'})

@admin_bp.route('/professionals/<int:prof_id>/reject', methods=['POST'])
@admin_required
def reject_professional(prof_id):
    # Implementação para rejeitar profissional
    return jsonify({'message': 'Profissional rejeitado com sucesso'})

# Rotas para gerenciamento de categorias
@admin_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': category.id,
        'name': category.name,
        'description': category.description
    } for category in categories])

@admin_bp.route('/categories', methods=['POST'])
@admin_required
def add_category():
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'error': 'Nome da categoria é obrigatório'}), 400

    category = Category(
        name=data['name'],
        description=data.get('description', '')
    )

    db.session.add(category)
    db.session.commit()

    return jsonify({
        'id': category.id,
        'name': category.name,
        'description': category.description
    }), 201

@admin_bp.route('/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.json
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']

    db.session.commit()

    return jsonify({
        'id': category.id,
        'name': category.name,
        'description': category.description
    })

@admin_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Categoria excluída com sucesso'})

# Rotas para gerenciamento de atividades
@admin_bp.route('/activities', methods=['POST'])
@admin_required
def add_activity():
    # Implementação para adicionar atividade
    return jsonify({'message': 'Atividade adicionada com sucesso'})

@admin_bp.route('/activities/<int:activity_id>', methods=['PUT'])
@admin_required
def update_activity(activity_id):
    # Implementação para atualizar atividade
    return jsonify({'message': 'Atividade atualizada com sucesso'})

@admin_bp.route('/activities/<int:activity_id>', methods=['DELETE'])
@admin_required
def delete_activity(activity_id):
    # Implementação para excluir atividade
    return jsonify({'message': 'Atividade excluída com sucesso'})
