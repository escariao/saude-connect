from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime

from src.models.user import db, User
from src.models.patient import Patient

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/register', methods=['POST'])
def register_patient():
    try:
        data = request.get_json()
        
        # Verificar se o email já está em uso
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Criar usuário
        new_user = User(
            email=data.get('email'),
            password=generate_password_hash(data.get('password')),
            name=data.get('name'),
            phone=data.get('phone'),
            user_type='patient'
        )
        
        db.session.add(new_user)
        db.session.flush()  # Para obter o ID do usuário
        
        # Processar data de nascimento
        birth_date = None
        if data.get('birth_date'):
            try:
                birth_date = datetime.strptime(data.get('birth_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        # Criar perfil de paciente
        new_patient = Patient(
            user_id=new_user.id,
            document_number=data.get('document_number'),
            birth_date=birth_date,
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state')
        )
        
        db.session.add(new_patient)
        db.session.commit()
        
        return jsonify({
            'message': 'Paciente cadastrado com sucesso!',
            'user_id': new_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
