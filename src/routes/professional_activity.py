from flask import Blueprint, request, jsonify
from ..models.professional_activity import ProfessionalActivity, db # Changed to relative import
from ..utils.auth import token_required # Changed to relative import

professional_activity_bp = Blueprint('professional_activity', __name__, url_prefix='/api/professional_activity')

@professional_activity_bp.route('/', methods=['GET'])
def list_professional_activities(): # Removed @token_required
    try:
        activities = ProfessionalActivity.query.all()
        return jsonify([a.serialize() for a in activities]), 200 # Use serialize()
    except Exception as e:
        # Consider logging the exception e for debugging
        return jsonify({'error': f'Erro ao listar atividades profissionais: {str(e)}'}), 500

@professional_activity_bp.route('/<int:id>', methods=['GET'])
def get_professional_activity(id): # Removed @token_required
    try:
        activity = ProfessionalActivity.query.get_or_404(id)
        return jsonify(activity.serialize()), 200 # Use serialize()
    except Exception as e:
        # Consider logging the exception e for debugging
        return jsonify({'error': f'Erro ao buscar atividade profissional: {str(e)}'}), 500

@professional_activity_bp.route('/', methods=['POST'])
@token_required
def create_professional_activity():
    try:
        data = request.json
        # Ensure 'activity_id' is provided in the request
        if 'activity_id' not in data:
            return jsonify({'error': 'activity_id is required'}), 400

        new_activity = ProfessionalActivity(
            professional_id=request.user_id,
            activity_id=data['activity_id'], # Use activity_id
            description=data.get('description', ''),
            price=data.get('price', 0.0), # Ensure float if model expects float
            availability=data.get('availability') # Added based on model's serialize method
        )
        db.session.add(new_activity)
        db.session.commit()
        # Use the model's serialize method for consistency
        return jsonify(new_activity.serialize()), 201 
    except Exception as e:
        db.session.rollback()
        # Consider logging the exception e for debugging
        return jsonify({'error': f'Erro ao criar atividade profissional: {str(e)}'}), 500

@professional_activity_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_professional_activity(id):
    try:
        activity = ProfessionalActivity.query.get_or_404(id)
        data = request.json

        # activity.activity_id = data.get('activity_id', activity.activity_id) # FKs usually not changed
        activity.description = data.get('description', activity.description)
        activity.price = data.get('price', activity.price)
        activity.availability = data.get('availability', activity.availability)

        db.session.commit()
        return jsonify(activity.serialize()), 200 # Use serialize()
    except Exception as e:
        db.session.rollback()
        # Consider logging the exception e for debugging
        return jsonify({'error': f'Erro ao atualizar atividade profissional: {str(e)}'}), 500

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
