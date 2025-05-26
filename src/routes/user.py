from flask import Blueprint, jsonify, request
from ..models.user import User, db # Changed to relative import
from ..utils.auth import token_required # Changed to relative import

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    try:
        if request.user_id != user_id:
            return jsonify({'error': 'Acesso não autorizado'}), 403

        user = User.query.get_or_404(user_id)
        result = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'user_type': user.user_type
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar usuário: {str(e)}'}), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    try:
        if request.user_id != user_id:
            return jsonify({'error': 'Acesso não autorizado'}), 403

        user = User.query.get_or_404(user_id)
        data = request.json

        user.name = data.get('name', user.name)
        user.phone = data.get('phone', user.phone)

        db.session.commit()
        return jsonify({'message': 'Usuário atualizado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar usuário: {str(e)}'}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    try:
        if request.user_id != user_id:
            return jsonify({'error': 'Acesso não autorizado'}), 403

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Usuário excluído com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao excluir usuário: {str(e)}'}), 500
