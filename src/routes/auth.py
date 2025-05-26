import os
import re
import uuid
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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

        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({'message': 'Email ou senha incorretos'}), 401

        token_payload = {
            'user_id': user.id,
            'user_type': user.user_type,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        token = token.decode('utf-8') if isinstance(token, bytes) else token

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
        if not request.form or not request.files:
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

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400

        diploma_file = request.files.get('diploma')
        if not diploma_file or diploma_file.filename == '':
            return jsonify({'error': 'Diploma é obrigatório'}), 400

        if not allowed_file(diploma_file.filename):
            return jsonify({'error': 'Formato de arquivo não permitido. Use PDF, PNG, JPG ou JPEG'}), 400

        filename = secure_filename(diploma_file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        diploma_file.save(os.path.join(UPLOAD_FOLDER, unique_filename))

        new_user = User(
            email=data['email'],
            password=generate_password_hash(data['password']),
            name=data['name'],
            phone=data.get('phone'),
            user_type='professional'
        )
        db.session.add(new_user)
        db.session.flush()

        document_number = data.get('document_number') or data['document'] or "Não informado"
        new_professional = Professional(
            user_id=new_user.id,
            document_number=document_number,
            diploma_file=unique_filename,
            bio=data.get('bio', ''),
            approval_status='pending'
        )
        db.session.add(new_professional)
        db.session.flush()

        activity_ids = request.form.getlist('activity_ids[]') # Expecting IDs now
        descriptions = request.form.getlist('descriptions[]') # Assuming these still align by index
        # experience_years is not a field in ProfessionalActivity model based on previous file reading.
        # If it were, it would be: experience_years = request.form.getlist('experience_years[]')
        prices = request.form.getlist('prices[]') # Assuming these still align by index
        availabilities = request.form.getlist('availabilities[]') # Assuming this might be provided

        # If `activity_ids` is empty, the old logic created a default activity.
        # With activity_id being mandatory, this needs a valid ID or this block should be removed/rethought.
        # For now, if no activity_ids are provided, no ProfessionalActivity will be created from this loop.
        # A real application might require at least one activity or have a default general activity_id.
        if activity_ids:
            for i, activity_id_str in enumerate(activity_ids):
                try:
                    activity_id = int(activity_id_str)
                    # Optional: Check if Activity with this ID exists
                    # activity = Activity.query.get(activity_id)
                    # if not activity:
                    #     # Handle error: activity ID not found
                    #     continue 

                    prof_activity = ProfessionalActivity(
                        professional_id=new_professional.id,
                        activity_id=activity_id, # Use the new foreign key
                        description=descriptions[i] if i < len(descriptions) else None,
                        price=float(prices[i]) if i < len(prices) and prices[i] else None,
                        availability=availabilities[i] if i < len(availabilities) else None
                        # experience_years is not in ProfessionalActivity model.
                    )
                    db.session.add(prof_activity)
                except ValueError:
                    # Handle error: activity_id_str is not a valid integer
                    current_app.logger.warning(f"Invalid activity_id received: {activity_id_str}")
                    continue 
        # else:
            # If activities are mandatory, you might want to return an error here:
            # return jsonify({'error': 'At least one activity ID must be provided.'}), 400
            # Or, if there's a default activity to assign:
            # default_activity = Activity.query.filter_by(name="General Service").first()
            # if default_activity:
            #     prof_activity = ProfessionalActivity(...)
            #     db.session.add(prof_activity)

        db.session.commit()
        return jsonify({'message': 'Profissional cadastrado com sucesso! Aguarde a aprovação do administrador.', 'user_id': new_user.id}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro interno ao cadastrar profissional.'}), 500

@auth_bp.route('/register/patient', methods=['POST'])
def register_patient():
    try:
        if request.is_json:
            data = request.get_json()
        elif request.form:
            data = request.form.to_dict()
        else:
            return jsonify({'error': 'Formato de dados inválido. Envie JSON ou formulário.'}), 400

        required_fields = ['email', 'password', 'name', 'document']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'O campo {field} é obrigatório'}), 400

        if not validate_email(data['email']):
            return jsonify({'error': 'Email inválido.'}), 400

        if len(data['password']) < 6:
            return jsonify({'error': 'Senha deve ter no mínimo 6 caracteres.'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400

        new_user = User(
            email=data['email'],
            password=generate_password_hash(data['password']),
            name=data['name'],
            phone=data.get('phone'),
            user_type='patient'
        )
        db.session.add(new_user)
        db.session.flush()

        from src.models.patient import Patient

        document_number = data.get('document_number') or data['document'] or "Não informado"
        birth_date = None
        if data.get('birth_date'):
            for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                try:
                    birth_date = datetime.strptime(data['birth_date'], fmt).date()
                    break
                except ValueError:
                    continue

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

        return jsonify({'message': 'Paciente cadastrado com sucesso!', 'user_id': new_user.id}), 201
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
