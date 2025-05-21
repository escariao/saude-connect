from flask import Blueprint, request, jsonify
from sqlalchemy import distinct

from src.models.user import db, User
from src.models.professional import Professional, Activity, ProfessionalActivity
from src.models.category import Category

search_bp = Blueprint('search', __name__)

@search_bp.route('/professionals', methods=['GET'])
def search_professionals():
    try:
        # Parâmetros de busca
        activity_id = request.args.get('activity_id')
        category = request.args.get('category')
        
        # Base query - apenas profissionais aprovados
        query = Professional.query.filter_by(approval_status='approved')
        
        # Filtrar por atividade específica
        if activity_id:
            query = query.join(ProfessionalActivity).filter(ProfessionalActivity.activity_id == activity_id)
        
        # Filtrar por categoria de atividade
        if category:
            query = query.join(ProfessionalActivity).join(Activity).filter(Activity.category == category)
        
        professionals = query.all()
        
        result = []
        for prof in professionals:
            user = User.query.get(prof.user_id)
            if user:
                prof_data = {
                    'id': prof.id,
                    'name': user.name,
                    'phone': user.phone,
                    'bio': prof.bio,
                    'activities': [{
                        'id': pa.id,
                        'activity_name': pa.activity.name,
                        'category': pa.activity.category,
                        'description': pa.description,
                        'experience_years': pa.experience_years,
                        'price': pa.price
                    } for pa in prof.activities]
                }
                result.append(prof_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_bp.route('/activities', methods=['GET'])
def get_activities():
    try:
        activities = Activity.query.all()
        return jsonify([{
            'id': activity.id,
            'name': activity.name,
            'description': activity.description,
            'category_id': activity.category_id,
            'category': Category.query.get(activity.category_id).name if activity.category_id else None
        } for activity in activities]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_bp.route('/activities/categories', methods=['GET'])
def get_activity_categories():
    try:
        # Obter categorias únicas
        categories = db.session.query(distinct(Category.name)).all()
        return jsonify([category[0] for category in categories if category[0]]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_bp.route('/professional/<int:professional_id>', methods=['GET'])
def get_professional_details(professional_id):
    try:
        prof = Professional.query.get(professional_id)
        if not prof:
            return jsonify({'error': 'Profissional não encontrado'}), 404
            
        user = User.query.get(prof.user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        prof_data = {
            'id': prof.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'bio': prof.bio,
            'activities': [{
                'id': pa.id,
                'activity_id': pa.activity_id,
                'activity_name': pa.activity.name,
                'category': pa.activity.category,
                'description': pa.description,
                'experience_years': pa.experience_years,
                'price': pa.price
            } for pa in prof.activities]
        }
        
        return jsonify(prof_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
