from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import jwt

from src.models.user import db, User
from src.models.patient import Patient

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/register', methods=['POST'])
def register_patient():
    try:
        data = request.get_json()
        
        # Verificar campos obrigatórios
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'O campo {field} é obrigatório'}), 400
        
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

@patient_bp.route('/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    try:
        # Verificar autenticação
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autenticação não fornecido'}), 401
            
        token = auth_header.split(' ')[1]
        
        try:
            # Decodificar token
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            
            # Verificar se o usuário está acessando seu próprio perfil ou é admin
            if user_id != patient_id and payload.get('user_type') != 'admin':
                return jsonify({'error': 'Acesso não autorizado'}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Buscar paciente
        patient = Patient.query.filter_by(user_id=patient_id).first()
        if not patient:
            return jsonify({'error': 'Paciente não encontrado'}), 404
            
        user = User.query.get(patient_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        # Montar resposta
        patient_data = {
            'id': patient.id,
            'user_id': patient.user_id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'document_number': patient.document_number,
            'birth_date': patient.birth_date.strftime('%Y-%m-%d') if patient.birth_date else None,
            'address': patient.address,
            'city': patient.city,
            'state': patient.state
        }
        
        return jsonify(patient_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    try:
        # Verificar autenticação
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autenticação não fornecido'}), 401
            
        token = auth_header.split(' ')[1]
        
        try:
            # Decodificar token
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            
            # Verificar se o usuário está atualizando seu próprio perfil
            if user_id != patient_id:
                return jsonify({'error': 'Acesso não autorizado'}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        data = request.get_json()
        
        # Buscar paciente
        patient = Patient.query.filter_by(user_id=patient_id).first()
        if not patient:
            return jsonify({'error': 'Paciente não encontrado'}), 404
            
        user = User.query.get(patient_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        # Atualizar dados do usuário
        if data.get('name'):
            user.name = data.get('name')
        if data.get('phone'):
            user.phone = data.get('phone')
            
        # Atualizar dados do paciente
        if data.get('document_number'):
            patient.document_number = data.get('document_number')
            
        if data.get('birth_date'):
            try:
                patient.birth_date = datetime.strptime(data.get('birth_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
                
        if data.get('address'):
            patient.address = data.get('address')
        if data.get('city'):
            patient.city = data.get('city')
        if data.get('state'):
            patient.state = data.get('state')
            
        db.session.commit()
        
        return jsonify({'message': 'Perfil atualizado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
