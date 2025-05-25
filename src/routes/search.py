from flask import Blueprint, request, jsonify
from sqlalchemy import exc
from src.models.user import db, User
from src.models.professional import Professional, Activity, ProfessionalActivity
from src.models.category import Category
from src.utils.auth import token_required

search_bp = Blueprint('search', __name__)

FIXED_CATEGORIES = [
    "Acupunturista", "Auxiliar de Saúde Bucal", "Cuidador", "Dentista", "Doula",
    "Educador Físico", "Enfermeiro", "Farmacêutico Clínico", "Fisioterapeuta", "Fonoaudiólogo",
    "Maqueiro", "Massoterapeuta", "Nutricionista", "Podólogo", "Psicólogo", "Técnico de Enfermagem",
    "Técnico em Análises Clínicas", "Técnico em Radiologia", "Terapeuta Ocupacional"
]


@search_bp.route('/professionals', methods=['GET'])
@token_required
def search_professionals():
    """Buscar profissionais com filtros opcionais."""
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
                for pa in prof.activities:
                    activity_data = {
                        'id': pa.id,
                        'activity_name': getattr(pa, 'activity_name', 'Atividade não especificada'),
                        'description': getattr(pa, 'description', ''),
                        'experience_years': getattr(pa, 'experience_years', 0),
                        'price': getattr(pa, 'price', 0)
                    }

                    if getattr(pa, 'activity_id', None):
                        activity = Activity.query.get(pa.activity_id)
                        if activity:
                            activity_data['activity_id'] = activity.id
                            activity_data['activity_name'] = activity.name
                            if getattr(activity, 'category_id', None):
                                category_obj = Category.query.get(activity.category_id)
                                if category_obj:
                                    activity_data['category'] = category_obj.name

                    activities_data.append(activity_data)

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
        print(f"Erro ao buscar profissionais: {e}")
        return jsonify([]), 200


@search_bp.route('/activities', methods=['GET'])
@token_required
def get_activities():
    """Buscar todas as atividades disponíveis."""
    try:
        inspector = db.inspect(db.engine)
        if 'activities' not in inspector.get_table_names():
            return jsonify([]), 200

        activities = Activity.query.all()
        result = []

        for activity in activities:
            category_name = None
            if getattr(activity, 'category_id', None):
                category_obj = Category.query.get(activity.category_id)
                if category_obj:
                    category_name = category_obj.name

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
        print(f"Erro de banco de dados ao buscar atividades: {db_error}")
        return jsonify([]), 200
    except Exception as e:
        print(f"Erro ao buscar atividades: {e}")
        return jsonify([]), 200


@search_bp.route('/categories', methods=['GET'])
@token_required
def get_categories():
    """Buscar todas as categorias fixas."""
    try:
        categories = [{
            'id': i,
            'name': category_name,
            'description': f'Profissionais da área de {category_name}'
        } for i, category_name in enumerate(FIXED_CATEGORIES, 1)]

        return jsonify(categories), 200

    except Exception as e:
        print(f"Erro ao buscar categorias: {e}")
        return jsonify([{
            'id': i,
            'name': category_name,
            'description': f'Profissionais da área de {category_name}'
        } for i, category_name in enumerate(FIXED_CATEGORIES, 1)]), 200


@search_bp.route('/professional/<int:professional_id>', methods=['GET'])
@token_required
def get_professional_details(professional_id):
    """Buscar detalhes de um profissional específico."""
    try:
        prof = Professional.query.get(professional_id)
        if not prof:
            return jsonify({'message': 'Profissional não encontrado'}), 404

        user = User.query.get(prof.user_id)
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404

        activities_data = []
        for pa in prof.activities:
            activity_data = {
                'id': pa.id,
                'activity_name': getattr(pa, 'activity_name', 'Atividade não especificada'),
                'description': getattr(pa, 'description', ''),
                'experience_years': getattr(pa, 'experience_years', 0),
                'price': getattr(pa, 'price', 0)
            }

            if getattr(pa, 'activity_id', None):
                activity = Activity.query.get(pa.activity_id)
                if activity:
                    activity_data['activity_id'] = activity.id
                    activity_data['activity_name'] = activity.name
                    if getattr(activity, 'category_id', None):
                        category_obj = Category.query.get(activity.category_id)
                        if category_obj:
                            activity_data['category'] = category_obj.name

            activities_data.append(activity_data)

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

    except Exception:
        return jsonify({'message': 'Erro ao buscar detalhes do profissional. Tente novamente mais tarde.'}), 500
