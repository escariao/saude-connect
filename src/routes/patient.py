from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.patient import Patient
from src.utils.auth import token_required

patient_bp = Blueprint('patient', __name__)


@patient_bp.route('/', methods=['POST'])
@token_required
def create_patient():
    """Criar perfil de paciente vinculado ao usuário autenticado."""
    try:
        data = request.get_json()
        if 'phone' not in data:
            return jsonify({'error': 'phone is required'}), 400

        patient = Patient(
            user_id=request.user_id,
            phone=data['phone'],
            document=data.get('document'),
            birth_date=data.get('birth_date'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state')
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify({'message': 'Paciente criado com sucesso', 'id': patient.id}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro interno ao criar paciente'}), 500


@patient_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_patient(user_id):
    """Obter informações do paciente vinculado ao usuário autenticado."""
    try:
        if request.user_id != user_id:
            return jsonify({'error': 'Acesso não autorizado'}), 403

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
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro interno ao buscar paciente'}), 500
