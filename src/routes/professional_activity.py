from flask import Blueprint, request, jsonify
from src.models.professional_activity import ProfessionalActivity, db
from src.utils.auth import token_required

professional_activity_bp = Blueprint('professional_activity', __name__, url_prefix='/api/professional_activity')

@professional_activity_bp.route('/', methods=['GET'])
def list_professional_activities():
    try:
        activities = ProfessionalActivity.query.all()
        return jsonify([a.to_dict() for a in activities]), 200
    except Exception:
        return jsonify({'error': 'Erro ao listar atividades profissionais.'}), 500

@professional_activity_bp.route('/<int:id>', methods=['GET'])
def get_professional_activity(id):
    try:
        activity = ProfessionalActivity.query.get_or_404(id)
        return jsonify(activity.to_dict()), 200
    except Exception:
        return jsonify({'error': 'Erro ao buscar atividade profissional.'}), 500

@professional_activity_bp.route('/', methods=['POST'])
@token_required
def create_professional_activity():
    try:
        data = request.json
        new_activity = ProfessionalActivity(
            professional_id=request.user_id,  # ID do profissional via token
            activity_name=data['activity_name'],
            description=data.get('description', ''),
            price=data.get('price', 0.0),
            availability=data.get('availability', 'Horário a combinar')
        )
        db.session.add(new_activity)
        db.session.commit()
        return jsonify(new_activity.to_dict()), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar atividade profissional.'}), 500

@professional_activity_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_professional_activity(id):
    try:
        activity = ProfessionalActivity.query.get_or_404(id)
        data = request.json

        activity.activity_name = data.get('activity_name', activity.activity_name)
        activity.description = data.get('description', activity.description)
        activity.price = data.get('price', activity.price)
        activity.availability = data.get('availability', activity.availability)

        db.session.commit()
        return jsonify(activity.to_dict()), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar atividade profissional.'}), 500

@professional_activity_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_professional_activity(id):
    try:
        activity = ProfessionalActivity.query.get_or_404(id)
        db.session.delete(activity)
        db.session.commit()
        return jsonify({'message': 'Atividade profissional excluída com sucesso.'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao excluir atividade profissional.'}), 500
