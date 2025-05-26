from flask import Blueprint, request, jsonify
from ..models.professional import Professional, db # Changed to relative import
from ..utils.auth import token_required # Changed to relative import

professional_bp = Blueprint('professional', __name__, url_prefix='/api/professional')

@professional_bp.route('/', methods=['GET'])
@token_required
def list_professionals():
    try:
        professionals = Professional.query.all()
        return jsonify([{
            'id': prof.id,
            'user_id': prof.user_id,
            'document_number': prof.document_number,
            'bio': prof.bio,
            'approval_status': prof.approval_status
        } for prof in professionals]), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao listar profissionais: {str(e)}'}), 500

@professional_bp.route('/<int:professional_id>', methods=['GET'])
@token_required
def get_professional(professional_id):
    try:
        prof = Professional.query.get_or_404(professional_id)
        result = {
            'id': prof.id,
            'user_id': prof.user_id,
            'document_number': prof.document_number,
            'bio': prof.bio,
            'approval_status': prof.approval_status
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar profissional: {str(e)}'}), 500

@professional_bp.route('/<int:professional_id>', methods=['PUT'])
@token_required
def update_professional(professional_id):
    try:
        prof = Professional.query.get_or_404(professional_id)
        data = request.json

        prof.bio = data.get('bio', prof.bio)
        prof.approval_status = data.get('approval_status', prof.approval_status)

        db.session.commit()
        return jsonify({'message': 'Profissional atualizado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar profissional: {str(e)}'}), 500

@professional_bp.route('/<int:professional_id>', methods=['DELETE'])
@token_required
def delete_professional(professional_id):
    try:
        prof = Professional.query.get_or_404(professional_id)
        db.session.delete(prof)
        db.session.commit()
        return jsonify({'message': 'Profissional excluído com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao excluir profissional: {str(e)}'}), 500
