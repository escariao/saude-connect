from flask import Blueprint, request, jsonify, current_app
import os
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime, timedelta

from src.models.user import db, User
from src.models.professional import Professional, Activity, ProfessionalActivity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Dados de login incompletos'}), 400
            
        user = User.query.filter_by(email=data.get('email')).first()
        
        if not user or not check_password_hash(user.password, data.get('password')):
            return jsonify({'message': 'Email ou senha incorretos'}), 401
            
        # Gerar token JWT
        token_payload = {
            'user_id': user.id,
            'user_type': user.user_type,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        
        token = jwt.encode(
            token_payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro no login: {str(e)}'}), 500

# Configuração para upload de arquivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Criar diretório de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/register/professional', methods=['POST'])
def register_professional():
    try:
        data = request.form.to_dict()
        
        # Verificar se o email já está em uso
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Verificar se o diploma foi enviado
        if 'diploma' not in request.files:
            return jsonify({'error': 'Diploma é obrigatório'}), 400
            
        diploma_file = request.files['diploma']
        if diploma_file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
            
        if not allowed_file(diploma_file.filename):
            return jsonify({'error': 'Formato de arquivo não permitido. Use PDF, PNG, JPG ou JPEG'}), 400
        
        # Salvar o arquivo com nome único
        filename = secure_filename(diploma_file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        diploma_file.save(file_path)
        
        # Criar usuário
        new_user = User(
            email=data.get('email'),
            password=generate_password_hash(data.get('password')),
            name=data.get('name'),
            phone=data.get('phone'),
            user_type='professional'
        )
        
        db.session.add(new_user)
        db.session.flush()  # Para obter o ID do usuário
        
        # Criar perfil profissional
        new_professional = Professional(
            user_id=new_user.id,
            document_number=data.get('document_number'),
            diploma_file=unique_filename,
            bio=data.get('bio'),
            approval_status='pending'
        )
        
        db.session.add(new_professional)
        db.session.flush()  # Para obter o ID do profissional
        
        # Processar atividades
        activities = request.form.getlist('activities[]')
        descriptions = request.form.getlist('descriptions[]')
        experience_years = request.form.getlist('experience_years[]')
        prices = request.form.getlist('prices[]')
        
        for i, activity_id in enumerate(activities):
            # Verificar se a atividade existe
            activity = Activity.query.get(activity_id)
            if not activity:
                continue
                
            # Adicionar atividade ao profissional
            prof_activity = ProfessionalActivity(
                professional_id=new_professional.id,
                activity_id=activity_id,
                description=descriptions[i] if i < len(descriptions) else None,
                experience_years=experience_years[i] if i < len(experience_years) else None,
                price=prices[i] if i < len(prices) else None
            )
            
            db.session.add(prof_activity)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profissional cadastrado com sucesso! Aguarde a aprovação do administrador.',
            'user_id': new_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    return jsonify([{
        'id': activity.id,
        'name': activity.name,
        'description': activity.description,
        'category': activity.category
    } for activity in activities]), 200
