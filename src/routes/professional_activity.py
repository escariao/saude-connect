from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.professional_activity import ProfessionalActivity

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/', methods=['POST'])
def create_activity():
    try:
        data = request.get_json()
        required_fields = ['professional_id', 'activity_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        activity = ProfessionalActivity(
            professional_id=data['professional_id'],
            activity_name=data['activity_name'],
            description=data.get('description'),
            price=data.get('price'),
            availability=data.get('availability')
        )
        db.session.add(activity)
        db.session.commit()
        return jsonify({'message': 'Activity created', 'id': activity.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/<int:id>', methods=['GET'])
def get_activity(id):
    activity = ProfessionalActivity.query.get(id)
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    return jsonify(activity.to_dict()), 200

@activity_bp.route('/', methods=['GET'])
def list_activities():
    activities = ProfessionalActivity.query.all()
    return jsonify([a.to_dict() for a in activities]), 200

@activity_bp.route('/<int:id>', methods=['PATCH'])
def update_activity(id):
    try:
        activity = ProfessionalActivity.query.get(id)
        if not activity:
            return jsonify({'error': 'Activity not found'}), 404

        data = request.get_json()
        for key in ['activity_name', 'description', 'price', 'availability']:
            if key in data:
                setattr(activity, key, data[key])
        db.session.commit()
        return jsonify({'message': 'Activity updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/<int:id>', methods=['DELETE'])
def delete_activity(id):
    try:
        activity = ProfessionalActivity.query.get(id)
        if not activity:
            return jsonify({'error': 'Activity not found'}), 404
        db.session.delete(activity)
        db.session.commit()
        return jsonify({'message': 'Activity deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
