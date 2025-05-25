from flask import Blueprint, request, jsonify
from sqlalchemy import distinct, exc

from src.models.user import db, User
from src.models.professional import Professional, Activity, ProfessionalActivity
from src.models.category import Category
from src.utils.auth import token_required  # ✅ Adicionada importação do decorator

search_bp = Blueprint('search', __name__)

# Lista de categorias fixas em ordem alfabética
FIXED_CATEGORIES = [
    "Acupunturista", "Auxiliar de Saúde Bucal", "Cuidador", "Dentista", "Doula",
    "Educador Físico", "Enfermeiro", "Farmacêutico Clínico", "Fisioterapeuta", "Fonoaudiólogo",
    "Maqueiro", "Massoterapeuta", "Nutricionista", "Podólogo", "Psicólogo", "Técnico de Enfermagem",
    "Técnico em Análises Clínicas", "Técnico em Radiologia", "Terapeuta Ocupacional"
]

@search_bp.route('/professionals', methods=['GET'])
@token_required  # ✅ Proteção aplicada
def search_professionals():
    try:
        activity_id = request.args.get('activity_id')
        category = request.args.get('category')
        name = request.args.get('name')
        
        query = Professional.query.filter_by(approval_status='approved')
        
        if activity_id:
            query = query.join(ProfessionalActivity).filter(ProfessionalActivity.activity_id == activity_id)
        
        if category and category.lower() != 'todas':
            query = query.join(ProfessionalActivity).join(Activity).join(Category).filter(Category.name == category)
        
        professionals = query.all()
        
        result = []
        for prof in professionals:
            user = User.query.get(prof.user_id)
            if user:
                if name and name.lower() not in user.name.lower():
                    continue
                    
                activities_data = []
                try:
                    for pa in prof.activities:
                        activity_data = {
                            'id': pa.id,
                            'activity_name': getattr(pa, 'activity_name', 'Atividade não especificada'),
                            'description': getattr(pa, 'description', ''),
                            'experience_years': getattr(pa, 'experience_years', 0),
                            'price': getattr(pa, 'price', 0)
                        }
                        
                        if hasattr(pa, 'activity_id') and pa.activity_id:
                            try:
                                activity = Activity.query.get(pa.activity_id)
                                if activity:
                                    activity_data['activity_id'] = activity.id
                                    activity_data['activity_name'] = activity.name
                                    
                                    if hasattr(activity, 'category_id') and activity.category_id:
                                        category = Category.query.get(activity.category_id)
                                        if category:
                                            activity_data['category'] = category.name
                            except:
                                pass
                                
                        activities_data.append(activity_data)
                except Exception as activity_error:
                    print(f"Erro ao processar atividades do profissional {prof.id}: {str(activity_error)}")
                    activities_data = []
                
                prof_data = {
                    'id': prof.id,
                    'user_id': prof.user_id,
                    'name': user.name,
                    'phone': user.phone,
                    'bio': getattr(prof, 'bio', ''),
                    'activities': activities_data
                }
                result.append(prof_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Erro ao buscar profissionais: {str(e)}")
        return jsonify([]), 200

@search_bp.route('/activities', methods=['GET'])
@token_required  # ✅ Proteção aplicada
def get_activities():
    try:
        inspector = db.inspect(db.engine)
        if 'activities' not in inspector.get_table_names():
            print("Tabela 'activities' não existe no banco de dados")
            return jsonify([]), 200
            
        activities = Activity.query.all()
        
        if not activities:
            return jsonify([]), 200
            
        result = []
        for activity in activities:
            category_name = None
            if hasattr(activity, 'category_id') and activity.category_id:
                try:
                    category = Category.query.get(activity.category_id)
                    if category:
                        category_name = category.name
                except:
                    pass
                    
            activity_data = {
                'id': activity.id,
                'name': activity.name,
                'description': getattr(activity, 'description', ''),
                'category_id': getattr(activity, 'category_id', None),
                'category': category_name
            }
            result.append(activity_data)
            
        return jsonify(result), 200
        
    except exc.SQLAlchemyError as db_error:
        print(f"Erro de banco de dados ao buscar atividades: {str(db_error)}")
        return jsonify([]), 200
    except Exception as e:
        print(f"Erro ao buscar atividades: {str(e)}")
        return jsonify([]), 200

@search_bp.route('/categories', methods=['GET'])
@token_required  # ✅ Proteção aplicada
def get_categories():
    try:
        categories = []
        for i, category_name in enumerate(FIXED_CATEGORIES, 1):
            categories.append({
                'id': i,
                'name': category_name,
                'description': f'Profissionais da área de {category_name}'
            })
            
        return jsonify(categories), 200
        
    except Exception as e:
        print(f"Erro ao buscar categorias: {str(e)}")
        categories = []
        for i, category_name in enumerate(FIXED_CATEGORIES, 1):
            categories.append({
                'id': i,
                'name': category_name,
                'description': f'Profissionais da área de {category_name}'
            })
        return jsonify(categories), 200

@search_bp.route('/professional/<int:professional_id>', methods=['GET'])
@token_required  # ✅ Proteção aplicada
def get_professional_details(professional_id):
    try:
        prof = Professional.query.get(professional_id)
        if not prof:
            return jsonify({'message': 'Profissional não encontrado'}), 404
            
        user = User.query.get(prof.user_id)
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
            
        activities_data = []
        try:
            for pa in prof.activities:
                activity_data = {
                    'id': pa.id,
                    'activity_name': getattr(pa, 'activity_name', 'Atividade não especificada'),
                    'description': getattr(pa, 'description', ''),
                    'experience_years': getattr(pa, 'experience_years', 0),
                    'price': getattr(pa, 'price', 0)
                }
                
                if hasattr(pa, 'activity_id') and pa.activity_id:
                    try:
                        activity = Activity.query.get(pa.activity_id)
                        if activity:
                            activity_data['activity_id'] = activity.id
                            activity_data['activity_name'] = activity.name
                            
                            if hasattr(activity, 'category_id') and activity.category_id:
                                category = Category.query.get(activity.category_id)
                                if category:
                                    activity_data['category'] = category.name
                    except:
                        pass
                        
                activities_data.append(activity_data)
        except Exception as activity_error:
            print(f"Erro ao processar atividades do profissional {prof.id}: {str(activity_error)}")
            activities_data = []
            
        prof_data = {
            'id': prof.id,
            'user_id': prof.user_id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'bio': getattr(prof, 'bio', ''),
            'activities': activities_data
        }
        
        return jsonify(prof_data), 200
        
    except Exception as e:
        return jsonify({'message': 'Erro ao buscar detalhes do profissional. Tente novamente mais tarde.'}), 500
