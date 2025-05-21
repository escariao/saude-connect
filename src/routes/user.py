from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps

from src.models.user import db, User
from src.models.professional import Professional, Activity, ProfessionalActivity
from src.models.patient import Patient

user_bp = Blueprint('user', __name__)

# Função para verificar token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401
            
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Usuário não encontrado'}), 401
        except:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
    user = User.query.filter_by(email=data.get('email')).first()
    
    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({'error': 'Email ou senha incorretos'}), 401
        
    # Gerar token JWT
    token = jwt.encode({
        'user_id': user.id,
        'user_type': user.user_type,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'user_type': user.user_type
        }
    }), 200

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    user_data = {
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'phone': current_user.phone,
        'user_type': current_user.user_type
    }
    
    if current_user.user_type == 'professional':
        professional = current_user.professional
        if professional:
            user_data['professional'] = {
                'document_number': professional.document_number,
                'bio': professional.bio,
                'approval_status': professional.approval_status,
                'activities': [{
                    'id': pa.id,
                    'activity_name': pa.activity.name,
                    'description': pa.description,
                    'experience_years': pa.experience_years,
                    'price': pa.price
                } for pa in professional.activities]
            }
    
    elif current_user.user_type == 'patient':
        patient = current_user.patient
        if patient:
            user_data['patient'] = {
                'document_number': patient.document_number,
                'birth_date': patient.birth_date.strftime('%Y-%m-%d') if patient.birth_date else None,
                'address': patient.address,
                'city': patient.city,
                'state': patient.state
            }
    
    return jsonify(user_data), 200
