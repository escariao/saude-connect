from flask import Blueprint, request, jsonify
from sqlalchemy import distinct, exc

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
    """
    Endpoint para buscar profissionais com filtros opcionais.
    Retorna um array vazio se não houver profissionais ou se ocorrer algum erro.
    """
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
        if category and category.lower() != 'todas':
            query = query.join(ProfessionalActivity).join(Activity).join(Category).filter(Category.name == category)
        
        professionals = query.all()
        
        result = []
        for prof in professionals:
            user = User.query.get(prof.user_id)
            if user:
                # Filtrar por nome se especificado
                if name and name.lower() not in user.name.lower():
                    continue
                    
                # Obter atividades do profissional de forma segura
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
                        
                        # Tentar obter informações da atividade se disponível
                        if hasattr(pa, 'activity_id') and pa.activity_id:
                            try:
                                activity = Activity.query.get(pa.activity_id)
                                if activity:
                                    activity_data['activity_id'] = activity.id
                                    activity_data['activity_name'] = activity.name
                                    
                                    # Tentar obter categoria se disponível
                                    if hasattr(activity, 'category_id') and activity.category_id:
                                        category = Category.query.get(activity.category_id)
                                        if category:
                                            activity_data['category'] = category.name
                            except:
                                # Se não conseguir obter a atividade, continua com os dados básicos
                                pass
                                
                        activities_data.append(activity_data)
                except Exception as activity_error:
                    # Se houver erro ao processar atividades, continua com lista vazia
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
        # Em caso de qualquer erro, retornar array vazio em vez de erro
        # Isso garante que o frontend não quebrará
        print(f"Erro ao buscar profissionais: {str(e)}")
        return jsonify([]), 200

@search_bp.route('/activities', methods=['GET'])
def get_activities():
    """
    Endpoint para buscar todas as atividades.
    Retorna um array vazio se não houver atividades ou se ocorrer algum erro.
    """
    try:
        # Verificar se a tabela existe antes de consultar
        inspector = db.inspect(db.engine)
        if 'activities' not in inspector.get_table_names():
            print("Tabela 'activities' não existe no banco de dados")
            return jsonify([]), 200
            
        # Tentar buscar as atividades
        activities = Activity.query.all()
        
        # Retornar array vazio se não houver atividades
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
                    # Se não conseguir obter a categoria, continua sem ela
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
        # Erro específico de banco de dados
        print(f"Erro de banco de dados ao buscar atividades: {str(db_error)}")
        return jsonify([]), 200
    except Exception as e:
        # Em caso de qualquer outro erro, retornar array vazio
        print(f"Erro ao buscar atividades: {str(e)}")
        return jsonify([]), 200

@search_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Endpoint para buscar todas as categorias.
    Sempre retorna a lista fixa de categorias, mesmo em caso de erro.
    """
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
        # Em caso de erro, retornar as categorias fixas de qualquer forma
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
def get_professional_details(professional_id):
    """
    Endpoint para buscar detalhes de um profissional específico.
    Retorna erro 404 se o profissional não for encontrado.
    """
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
                
                # Tentar obter informações da atividade se disponível
                if hasattr(pa, 'activity_id') and pa.activity_id:
                    try:
                        activity = Activity.query.get(pa.activity_id)
                        if activity:
                            activity_data['activity_id'] = activity.id
                            activity_data['activity_name'] = activity.name
                            
                            # Tentar obter categoria se disponível
                            if hasattr(activity, 'category_id') and activity.category_id:
                                category = Category.query.get(activity.category_id)
                                if category:
                                    activity_data['category'] = category.name
                    except:
                        # Se não conseguir obter a atividade, continua com os dados básicos
                        pass
                        
                activities_data.append(activity_data)
        except Exception as activity_error:
            # Se houver erro ao processar atividades, continua com lista vazia
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
