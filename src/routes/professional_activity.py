# src/routes/professional_activity.py

from flask import Blueprint, request, jsonify
from src.models.professional_activity import ProfessionalActivity, db

# Renomeando para activity_bp para corresponder à importação em main.py
activity_bp = Blueprint('professional_activity', __name__, url_prefix='/api/professional_activity')

from src.models.professional import Activity # Ensure Activity model is imported

@activity_bp.route('/', methods=['GET'])
def list_professional_activities():
    activities = ProfessionalActivity.query.all()
    return jsonify([a.serialize() for a in activities]), 200

@activity_bp.route('/<int:id>', methods=['GET'])
def get_professional_activity(id):
    activity = ProfessionalActivity.query.get_or_404(id)
    return jsonify(activity.serialize()), 200

@activity_bp.route('/', methods=['POST'])
def create_professional_activity():
    data = request.json
    if not data:
        return jsonify({"message": "Invalid input"}), 400

    professional_id = data.get('professional_id')
    activity_id = data.get('activity_id') # Expect activity_id

    if not professional_id or activity_id is None: # activity_id can be 0, so check for None
        return jsonify({"message": "Missing professional_id or activity_id"}), 400

    # Validate if the global Activity exists
    global_activity = Activity.query.get(activity_id)
    if not global_activity:
        return jsonify({"message": f"Activity with id {activity_id} not found"}), 404

    try:
        new_activity = ProfessionalActivity(
            professional_id=professional_id,
            activity_id=activity_id, # Use activity_id
            description=data.get('description'), # Allow null
            price=data.get('price'), # Allow null
            availability=data.get('availability') # Allow null
        )
        db.session.add(new_activity)
        db.session.commit()
        return jsonify(new_activity.serialize()), 201
    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"message": "Could not create professional activity", "error": str(e)}), 500
