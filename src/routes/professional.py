from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.professional import Professional

professional_bp = Blueprint('professional', __name__)

@professional_bp.route('/', methods=['POST'])
def create_professional():
    try:
        data = request.get_json()
        required_fields = ['user_id', 'category_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        professional = Professional(
            user_id=data['user_id'],
            category_id=data['category_id'],
            curriculum_file=data.get('curriculum_file'),
            phone=data.get('phone'),
            document=data.get('document')
        )

        db.session.add(professional)
        db.session.commit()

        return jsonify({'message': 'Professional created', 'id': professional.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
