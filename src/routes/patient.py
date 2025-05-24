
from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.patient import Patient

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/', methods=['POST'])
def create_patient():
    try:
        data = request.get_json()
        required_fields = ['user_id', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        patient = Patient(
            user_id=data['user_id'],
            phone=data['phone'],
            document=data.get('document'),
            birth_date=data.get('birth_date'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state')
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify({'message': 'Patient created', 'id': patient.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/<int:user_id>', methods=['GET'])
def get_patient(user_id):
    try:
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient:
            return jsonify({'error': 'Paciente não encontrado'}), 404
        result = {
            'id': patient.id,
            'phone': patient.phone,
            'document': patient.document,
            'birth_date': patient.birth_date.isoformat() if patient.birth_date else None,
            'address': patient.address,
            'city': patient.city,
            'state': patient.state
        }
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
