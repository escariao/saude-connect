from flask import Blueprint, request, jsonify
from sqlalchemy import distinct

from src.models.user import db, User
from src.models.professional import Professional, Activity, ProfessionalActivity
from src.models.category import Category

search_bp = Blueprint('search', __name__)

# Lista de categorias fixas em ordem alfabética
FIXED_CATEGORIES = [
    "Acupunturista",
    "Auxiliar de Saúde Bucal",
    "Cuidador",
    "Dentista",
    "Doula",
    "Educador Físico",
    "Enfermeiro",
    "Farmacêutico Clínico",
    "Fisioterapeuta",
    "Fonoaudiólogo",
    "Maqueiro",
    "Massoterapeuta",
    "Nutricionista",
    "Podólogo",
    "Psicólogo",
    "Técnico de Enfermagem",
    "Técnico em Análises Clínicas",
    "Técnico em Radiologia",
    "Terapeuta Ocupacional"
]

@search_bp.route('/professionals', methods=['GET'])
def search_professionals():
    try:
        # Parâmetros de busca
        activity_id = request.args.get('activity_id')
        category = request.args.get('category')
        name = request.args.get('name')
        
        # Base query - apenas profissionais aprovados
        query = Professional.query.filter_by(approval_status='approved')
        
        # Filtrar por atividade específica
        if activity_id:
            query = query.join(ProfessionalActivity).filter(ProfessionalActivity.activity_id == activity_id)
        
        # Filtrar por categoria de atividade
        if category:
            query = query.join(ProfessionalActivity).join(Activity).join(Category).filter(Category.name == category)
        
        professionals = query.all()
        
        result = []
        for prof in professionals:
            user = User.query.get(prof.user_id)
            if user:
                # Filtrar por nome se especificado
                if name and name.lower() not in user.name.lower():
                    continue
                    
                prof_data = {
                    'id': prof.id,
                    'user_id': prof.user_id,
                    'name': user.name,
                    'phone': user.phone,
                    'bio': prof.bio,
                    'activities': [{
                        'id': pa.id,
                        'activity_id': pa.activity_id,
                        'activity_name': pa.activity.name,
                        'category': Category.query.get(pa.activity.category_id).name if pa.activity.category_id else None,
                        'description': pa.description,
                        'experience_years': pa.experience_years,
                        'price': pa.price
                    } for pa in prof.activities]
                }
                result.append(prof_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Falha ao buscar profissionais: {str(e)}'}), 500

@search_bp.route('/activities', methods=['GET'])
def get_activities():
    try:
        activities = Activity.query.all()
        
        if not activities:
            return jsonify([]), 200
            
        result = []
        for activity in activities:
            category_name = None
            if activity.category_id:
                category = Category.query.get(activity.category_id)
                if category:
                    category_name = category.name
                    
            activity_data = {
                'id': activity.id,
                'name': activity.name,
                'description': activity.description,
                'category_id': activity.category_id,
                'category': category_name
            }
            result.append(activity_data)
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Falha ao buscar atividades: {str(e)}'}), 500

@search_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        # Retornar categorias fixas em vez de buscar do banco de dados
        categories = []
        for i, category_name in enumerate(FIXED_CATEGORIES, 1):
            categories.append({
                'id': i,
                'name': category_name,
                'description': f'Profissionais da área de {category_name}'
            })
            
        return jsonify(categories), 200
        
    except Exception as e:
        return jsonify({'error': f'Falha ao buscar categorias: {str(e)}'}), 500

@search_bp.route('/professional/<int:professional_id>', methods=['GET'])
def get_professional_details(professional_id):
    try:
        prof = Professional.query.get(professional_id)
        if not prof:
            return jsonify({'error': 'Profissional não encontrado'}), 404
            
        user = User.query.get(prof.user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        activities_data = []
        for pa in prof.activities:
            activity = Activity.query.get(pa.activity_id)
            if not activity:
                continue
                
            category_name = None
            if activity.category_id:
                category = Category.query.get(activity.category_id)
                if category:
                    category_name = category.name
                    
            activity_data = {
                'id': pa.id,
                'activity_id': pa.activity_id,
                'activity_name': activity.name,
                'category_id': activity.category_id,
                'category': category_name,
                'description': pa.description,
                'experience_years': pa.experience_years,
                'price': pa.price
            }
            activities_data.append(activity_data)
            
        prof_data = {
            'id': prof.id,
            'user_id': prof.user_id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'bio': prof.bio,
            'activities': activities_data
        }
        
        return jsonify(prof_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Falha ao buscar detalhes do profissional: {str(e)}'}), 500
