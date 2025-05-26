from flask import Blueprint, request, jsonify
from sqlalchemy import exc
from src.models.user import User, db
from src.models.professional import Professional, Activity, ProfessionalActivity
from src.models.category import Category
from src.utils.auth import token_required

search_bp = Blueprint('search', __name__, url_prefix='/api/search')

@search_bp.route('/professionals', methods=['GET'])
@token_required
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
            if not user:
                continue

            if name and name.lower() not in user.name.lower():
                continue

            activities_data = []
            for pa in prof.activities: # pa is a ProfessionalActivity instance
                activity_model = Activity.query.get(pa.activity_id)
                category_name = None
                activity_global_description = ''

                if activity_model:
                    activity_global_description = activity_model.description if activity_model.description else ''
                    if activity_model.category_id:
                        category_model = Category.query.get(activity_model.category_id)
                        if category_model:
                            category_name = category_model.name
                
                activity_data = {
                    'professional_activity_id': pa.id,
                    'activity_id': pa.activity_id,
                    'activity_name': activity_model.name if activity_model else 'Atividade Desconhecida',
                    'activity_description': activity_global_description,
                    'professional_description': pa.description,
                    'price': pa.price,
                    'availability': pa.availability, # Assuming pa has availability from ProfessionalActivity model
                    'category': category_name
                }
                activities_data.append(activity_data)

            prof_data = {
                'id': prof.id,
                'user_id': prof.user_id,
                'name': user.name,
                'phone': user.phone,
                'bio': prof.bio,
                'activities': activities_data
            }
            result.append(prof_data)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar profissionais: {str(e)}'}), 500

@search_bp.route('/activities', methods=['GET'])
@token_required
def get_activities():
    try:
        inspector = db.inspect(db.engine)
        if 'activities' not in inspector.get_table_names():
            return jsonify([]), 200

        activities = Activity.query.all()
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
                'description': activity.description or '',
                'category_id': activity.category_id,
                'category': category_name
            }
            result.append(activity_data)

        return jsonify(result), 200
    except exc.SQLAlchemyError as db_error:
        return jsonify({'error': f'Erro de banco de dados: {str(db_error)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar atividades: {str(e)}'}), 500

@search_bp.route('/categories', methods=['GET'])
@token_required
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories]), 200
    except Exception as e:
        # Log the error e
        return jsonify({'error': f'Erro ao buscar categorias: {str(e)}'}), 500

@search_bp.route('/professional/<int:professional_id>', methods=['GET'])
@token_required
def get_professional_details(professional_id):
    try:
        prof = Professional.query.get(professional_id)
        if not prof:
            return jsonify({'error': 'Profissional não encontrado'}), 404

        user = User.query.get(prof.user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        activities_data = []
            for pa in prof.activities: # pa is a ProfessionalActivity instance
                activity_model = Activity.query.get(pa.activity_id)
                category_name = None
                activity_global_description = ''

                if activity_model:
                    activity_global_description = activity_model.description if activity_model.description else ''
                    if activity_model.category_id:
                        category_model = Category.query.get(activity_model.category_id)
                        if category_model:
                            category_name = category_model.name
                
            activity_data = {
                    'professional_activity_id': pa.id,
                    'activity_id': pa.activity_id,
                    'activity_name': activity_model.name if activity_model else 'Atividade Desconhecida',
                    'activity_description': activity_global_description,
                    'professional_description': pa.description,
                    'price': pa.price,
                    'availability': pa.availability, # Assuming pa has availability from ProfessionalActivity model
                    'category': category_name
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
        return jsonify({'error': f'Erro ao buscar detalhes do profissional: {str(e)}'}), 500
