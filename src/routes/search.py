from flask import Blueprint, request, jsonify

from src.models.user import User
from src.models.professional import Professional, Activity, ProfessionalActivity

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

@search_bp.route('/activities/categories', methods=['GET'])
def get_activity_categories():
    try:
        # Obter categorias únicas
        categories = db.session.query(Activity.category).distinct().all()
        return jsonify([category[0] for category in categories if category[0]]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
