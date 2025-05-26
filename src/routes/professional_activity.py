# src/routes/professional_activity.py

from flask import Blueprint, request, jsonify
from src.models.professional_activity import ProfessionalActivity, db

# Renomeando para activity_bp para corresponder à importação em main.py
activity_bp = Blueprint('professional_activity', __name__, url_prefix='/api/professional_activity')

@activity_bp.route('/', methods=['GET'])
def list_professional_activities():
    activities = ProfessionalActivity.query.all()
    return jsonify([a.to_dict() for a in activities]), 200  # Usando to_dict em vez de serialize

@activity_bp.route('/<int:id>', methods=['GET'])
def get_professional_activity(id):
    activity = ProfessionalActivity.query.get_or_404(id)
    return jsonify(activity.to_dict()), 200  # Usando to_dict em vez de serialize

@activity_bp.route('/', methods=['POST'])
def create_professional_activity():
    data = request.json
    new_activity = ProfessionalActivity(
        professional_id=data['professional_id'],
        activity_name=data['activity_name'],  # Corrigido para corresponder ao modelo
        description=data.get('description', ''),
        price=data.get('price', 0),
        availability=data.get('availability', '')  # Adicionado campo availability
    )
    db.session.add(new_activity)
    db.session.commit()
    return jsonify(new_activity.to_dict()), 201  # Usando to_dict em vez de serialize
