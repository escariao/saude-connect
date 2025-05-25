from flask import Blueprint, request, jsonify, current_app
import os
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime, timedelta
import re

from src.models.user import db, User
from src.models.professional import Professional, Activity, ProfessionalActivity

auth_bp = Blueprint('auth', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Dados de login incompletos'}), 400
        
        user = User.query.filter_by(email=data.get('email')).first()
        
        if not user or not check_password_hash(user.password, data.get('password')):
            return jsonify({'message': 'Email ou senha incorretos'}), 401
        
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
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type
            }
        }), 200
    except Exception:
        return jsonify({'message': 'Erro interno ao realizar login.'}), 500

@auth_bp.route('/register/professional', methods=['POST'])
def register_professional():
    try:
        if not request.form and not request.files:
            return jsonify({'error': 'Dados de formulário não encontrados'}), 400
        
        data = request.form.to_dict()
        
        required_fields = ['email', 'password', 'name', 'document']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'O campo {field} é obrigatório'}), 400
        
        if not validate_email(data['email']):
            return jsonify({'error': 'Email inválido.'}), 400
        
        if len(data['password']) < 6:
            return jsonify({'error': 'Senha deve ter no mínimo 6 caracteres.'}), 400
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        if 'diploma' not in request.files:
            return jsonify({'error': 'Diploma é obrigatório'}), 400
        
        diploma_file = request.files['diploma']
        if diploma_file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(diploma_file.filename):
            return jsonify({'error': 'Formato de arquivo não permitido. Use PDF, PNG, JPG ou JPEG'}), 400
        
        filename = secure_filename(diploma_file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        diploma_file.save(file_path)
        
        new_user = User(
            email=data.get('email'),
            password=generate_password_hash(data.get('password')),
            name=data.get('name'),
            phone=data.get('phone'),
            user_type='professional'
        )
        
        db.session.add(new_user)
        db.session.flush()
        
        document_number = data.get('document_number', data.get('document', 'Não informado'))
        
        new_professional = Professional(
            user_id=new_user.id,
            document_number=document_number,
            diploma_file=unique_filename,
            bio=data.get('bio', ''),
            approval_status='pending'
        )
        
        db.session.add(new_professional)
        db.session.flush()
        
        activities = request.form.getlist('activities[]')
        descriptions = request.form.getlist('descriptions[]')
        experience_years = request.form.getlist('experience_years[]')
        prices = request.form.getlist('prices[]')
        
        if not activities:
            category_id = data.get('category_id')
            if category_id:
                prof_activity = ProfessionalActivity(
                    professional_id=new_professional.id,
                    activity_name=f"Serviço de {new_user.name}",
                    description=data.get('bio', 'Serviço profissional'),
                    experience_years=0,
                    price=0
                )
                db.session.add(prof_activity)
        else:
            for i, activity_name in enumerate(activities):
                prof_activity = ProfessionalActivity(
                    professional_id=new_professional.id,
                    activity_name=activity_name,
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
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro interno ao cadastrar profissional.'}), 500

@auth_bp.route('/register/patient', methods=['POST'])
def register_patient():
    try:
        if not request.is_json:
            if request.form:
                data = request.form.to_dict()
            else:
                return jsonify({'error': 'Formato de dados inválido. Envie JSON ou formulário.'}), 400
        else:
            data = request.get_json()
        
        required_fields = ['email', 'password', 'name', 'document']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'O campo {field} é obrigatório'}), 400
        
        if not validate_email(data['email']):
            return jsonify({'error': 'Email inválido.'}), 400
        
        if len(data['password']) < 6:
            return jsonify({'error': 'Senha deve ter no mínimo 6 caracteres.'}), 400
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        new_user = User(
            email=data.get('email'),
            password=generate_password_hash(data.get('password')),
            name=data.get('name'),
            phone=data.get('phone'),
            user_type='patient'
        )
        
        db.session.add(new_user)
        db.session.flush()
        
        from src.models.patient import Patient
        
        document_number = data.get('document_number', data.get('document', 'Não informado'))
        
        birth_date = None
        if data.get('birth_date'):
            try:
                birth_date = datetime.strptime(data.get('birth_date'), '%Y-%m-%d').date()
            except ValueError:
                try:
                    birth_date = datetime.strptime(data.get('birth_date'), '%d/%m/%Y').date()
                except ValueError:
                    birth_date = None
        
        new_patient = Patient(
            user_id=new_user.id,
            document_number=document_number,
            birth_date=birth_date,
            address=data.get('address', ''),
            city=data.get('city', ''),
            state=data.get('state', '')
        )
        
        db.session.add(new_patient)
        db.session.commit()
        
        return jsonify({
            'message': 'Paciente cadastrado com sucesso!',
            'user_id': new_user.id
        }), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro interno ao cadastrar paciente.'}), 500

@auth_bp.route('/activities', methods=['GET'])
def get_activities():
    try:
        inspector = db.inspect(db.engine)
        if 'activities' not in inspector.get_table_names():
            return jsonify([]), 200
        
        activities = Activity.query.all()
        return jsonify([{
            'id': activity.id,
            'name': activity.name,
            'description': activity.description,
            'category': activity.category_id
        } for activity in activities]), 200
    except Exception:
        return jsonify({'error': 'Erro ao buscar atividades.'}), 500
