from flask import Blueprint, request, jsonify
from src.models.professional import Professional, db
from src.utils.auth import token_required

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
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400

        # Authorization logic
        if request.user_type == 'admin':
            if 'bio' in data:
                prof.bio = data['bio']
            if 'approval_status' in data:
                # Validate approval_status if necessary (e.g., specific allowed values)
                allowed_statuses = ['pending', 'approved', 'rejected']
                if data['approval_status'] not in allowed_statuses:
                    return jsonify({'error': f'Status de aprovação inválido. Valores permitidos: {allowed_statuses}'}), 400
                prof.approval_status = data['approval_status']
        
        elif request.user_type == 'professional':
            # Check if the professional is updating their own profile
            if prof.user_id != request.user_id:
                return jsonify({'error': 'Não autorizado a atualizar este perfil'}), 403
            
            if 'bio' in data:
                prof.bio = data['bio']
            if 'approval_status' in data:
                # Professionals cannot change their own approval status
                return jsonify({'error': 'Você não tem permissão para alterar o status de aprovação.'}), 403
        
        else:
            # Other user types are not authorized
            return jsonify({'error': 'Não autorizado'}), 403

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
