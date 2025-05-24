# src/routes/professional_activity.py

from flask import Blueprint, request, jsonify
from src.models.professional_activity import ProfessionalActivity, db

professional_activity_bp = Blueprint('professional_activity', __name__, url_prefix='/api/professional_activity')

@professional_activity_bp.route('/', methods=['GET'])
def list_professional_activities():
    activities = ProfessionalActivity.query.all()
    return jsonify([a.serialize() for a in activities]), 200

@professional_activity_bp.route('/<int:id>', methods=['GET'])
def get_professional_activity(id):
    activity = ProfessionalActivity.query.get_or_404(id)
    return jsonify(activity.serialize()), 200

@professional_activity_bp.route('/', methods=['POST'])
def create_professional_activity():
    data = request.json
    new_activity = ProfessionalActivity(
        professional_id=data['professional_id'],
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        years_of_experience=data.get('years_of_experience', 0)
    )
    db.session.add(new_activity)
    db.session.commit()
    return jsonify(new_activity.serialize()), 201
