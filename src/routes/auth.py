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
        # Verificar se a requisição é JSON
        if not request.is_json:
            # Tentar obter dados do formulário se não for JSON
            if request.form:
                data = request.form.to_dict()
            else:
                return jsonify({'message': 'Formato de dados inválido. Envie JSON ou formulário.'}), 400
        else:
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
        # Verificar se a requisição contém dados de formulário
        if not request.form and not request.files:
            return jsonify({'error': 'Dados de formulário não encontrados'}), 400
            
        data = request.form.to_dict()
        
        # Verificar campos obrigatórios
        required_fields = ['email', 'password', 'name', 'document']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'O campo {field} é obrigatório'}), 400
        
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
        
        # Garantir que document_number não seja nulo
        document_number = data.get('document_number', data.get('document', ''))
        if not document_number:
            document_number = "Não informado"
        
        # Criar perfil profissional
        new_professional = Professional(
            user_id=new_user.id,
            document_number=document_number,
            diploma_file=unique_filename,
            bio=data.get('bio', ''),
            approval_status='pending'
        )
        
        db.session.add(new_professional)
        db.session.flush()  # Para obter o ID do profissional
        
        # Processar atividades selecionadas pelo profissional
        activity_ids = request.form.getlist('activity_ids[]')
        activity_descriptions = request.form.getlist('activity_descriptions[]')
        activity_prices = request.form.getlist('activity_prices[]')
        # availability = request.form.getlist('activity_availabilities[]') # Assuming availability is also per activity
        # experience_years = request.form.getlist('activity_experience_years[]') # Assuming experience is also per activity

        if activity_ids:
            for i, activity_id_str in enumerate(activity_ids):
                try:
                    activity_id = int(activity_id_str)
                    activity = Activity.query.get(activity_id)
                    if not activity:
                        # Opção: Logar um aviso, ignorar, ou retornar erro
                        # Para este exemplo, vamos ignorar atividades inválidas silenciosamente,
                        # mas em produção, um erro ou log seria melhor.
                        current_app.logger.warn(f"Tentativa de registrar atividade com ID inválido: {activity_id_str}")
                        continue

                    # Coletar detalhes específicos da atividade para este profissional
                    description = activity_descriptions[i] if i < len(activity_descriptions) else None
                    price_str = activity_prices[i] if i < len(activity_prices) else None
                    # availability_str = availability[i] if i < len(availability) else None
                    # experience_str = experience_years[i] if i < len(experience_years) else None
                    
                    price = None
                    if price_str:
                        try:
                            price = float(price_str)
                        except ValueError:
                            # Logar erro de conversão de preço
                            current_app.logger.warn(f"Valor de preço inválido para atividade {activity_id}: {price_str}")
                            # Decidir se deve continuar ou retornar erro
                    
                    # experience = None
                    # if experience_str:
                    #     try:
                    #         experience = int(experience_str)
                    #     except ValueError:
                    #         current_app.logger.warn(f"Valor de experiência inválido para atividade {activity_id}: {experience_str}")


                    prof_activity = ProfessionalActivity(
                        professional_id=new_professional.id,
                        activity_id=activity.id, # Usar o ID da atividade validada
                        description=description,
                        price=price
                        # availability=availability_str,
                        # experience_years=experience # Adicionar se o campo existir no modelo ProfessionalActivity
                    )
                    db.session.add(prof_activity)
                except ValueError:
                    current_app.logger.warn(f"ID de atividade inválido (não é um inteiro): {activity_id_str}")
                    continue # Pula para o próximo ID de atividade
        
        # Nota: A lógica de fallback para criar uma atividade padrão se nenhuma for fornecida foi removida
        # conforme a especificação do Sub-task 3.2.

        db.session.commit()
        
        return jsonify({
            'message': 'Profissional cadastrado com sucesso! Aguarde a aprovação do administrador.',
            'user_id': new_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register/patient', methods=['POST'])
def register_patient():
    try:
        # Verificar se a requisição é JSON
        if not request.is_json:
            # Tentar obter dados do formulário se não for JSON
            if request.form:
                data = request.form.to_dict()
            else:
                return jsonify({'error': 'Formato de dados inválido. Envie JSON ou formulário.'}), 400
        else:
            data = request.get_json()
        
        # Verificar campos obrigatórios
        required_fields = ['email', 'password', 'name', 'document']
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
            phone=data.get('phone', ''),
            user_type='patient'
        )
        
        db.session.add(new_user)
        db.session.flush()  # Para obter o ID do usuário
        
        # Importar Patient aqui para evitar importação circular
        from src.models.patient import Patient
        
        # Processar data de nascimento
        birth_date = None
        if data.get('birth_date'):
            try:
                birth_date = datetime.strptime(data.get('birth_date'), '%Y-%m-%d').date()
            except ValueError:
                # Tentar outro formato se o primeiro falhar
                try:
                    birth_date = datetime.strptime(data.get('birth_date'), '%d/%m/%Y').date()
                except ValueError:
                    birth_date = None
        
        # Criar perfil de paciente - usando document em vez de document_number
        new_patient = Patient(
            user_id=new_user.id,
            document=data.get('document', 'Não informado'),
            phone=data.get('phone', ''),
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
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
# The /activities route has been removed from auth_bp as per subtask 4.3
