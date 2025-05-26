from flask import Blueprint, request, jsonify
from ..models.professional_activity import ProfessionalActivity, db # Changed to relative import
from ..utils.auth import token_required # Changed to relative import

professional_activity_bp = Blueprint('professional_activity', __name__, url_prefix='/api/professional_activity')

@professional_activity_bp.route('/', methods=['GET'])
def list_professional_activities():
    try:
        activities = ProfessionalActivity.query.all()
        return jsonify([{
            'id': a.id,
            'professional_id': a.professional_id,
            'activity_name': a.activity_name,
            'description': a.description,
            'experience_years': a.experience_years,
            'price': a.price
        } for a in activities]), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao listar atividades profissionais: {str(e)}'}), 500

@professional_activity_bp.route('/<int:id>', methods=['GET'])
def get_professional_activity(id):
    try:
        activity = ProfessionalActivity.query.get_or_404(id)
        result = {
            'id': activity.id,
            'professional_id': activity.professional_id,
            'activity_name': activity.activity_name,
            'description': activity.description,
            'experience_years': activity.experience_years,
            'price': activity.price
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar atividade: {str(e)}'}), 500

@professional_activity_bp.route('/', methods=['POST'])
@token_required
def create_professional_activity():
    try:
        data = request.json
        new_activity = ProfessionalActivity(
            professional_id=request.user_id,  # assume que o user é profissional
            activity_name=data['activity_name'],
            description=data.get('description', ''),
            experience_years=data.get('experience_years', 0),
            price=data.get('price', 0)
        )
        db.session.add(new_activity)
        db.session.commit()
        return jsonify({'message': 'Atividade criada com sucesso!', 'id': new_activity.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar atividade: {str(e)}'}), 500

@professional_activity_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_professional_activity(id):
    try:
        activity = ProfessionalActivity.query.get_or_404(id)
        data = request.json

        activity.activity_name = data.get('activity_name', activity.activity_name)
        activity.description = data.get('description', activity.description)
        activity.experience_years = data.get('experience_years', activity.experience_years)
        activity.price = data.get('price', activity.price)

        db.session.commit()
        return jsonify({'message': 'Atividade atualizada com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar atividade: {str(e)}'}), 500

@professional_activity_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_professional_activity(id):
    try:
        activity = ProfessionalActivity.query.get_or_404(id)
        db.session.delete(activity)
        db.session.commit()
        return jsonify({'message': 'Atividade excluída com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao excluir atividade: {str(e)}'}), 500
