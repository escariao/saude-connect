from flask import Blueprint, request, jsonify
from src.models.user import User, db
from src.models.professional import Professional, Activity
from src.models.professional_activity import ProfessionalActivity # For checking usage in delete_activity
from src.models.category import Category
# from src.utils.auth import admin_required # Removed as per task
from datetime import datetime
from functools import wraps
import jwt
import os 
from flask import current_app

# Middleware para verificar se o usuário é administrador
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization') # More robust way to get header

        if auth_header and auth_header.startswith('Bearer '):
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Formato de token inválido. Use "Bearer <token>"'}), 401
        
        if not token:
            return jsonify({'error': 'Token de autenticação não fornecido ou malformado'}), 401

        try:
            # Use current_app.config for SECRET_KEY
            secret_key = current_app.config.get('SECRET_KEY')
            if not secret_key:
                # Fallback if not set in app config, though it should be
                secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_for_testing')

            data = jwt.decode(token, secret_key, algorithms=["HS256"])
            
            # Ensure 'user_type' is in the token payload
            if 'user_type' not in data:
                return jsonify({'error': 'Token inválido: user_type ausente'}), 401

            if data['user_type'] != 'admin':
                return jsonify({'error': 'Acesso restrito a administradores'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError: # Catches various JWT errors like invalid signature, malformed token
            return jsonify({'error': 'Token inválido ou malformado'}), 401
        except Exception as e: # Catch any other unexpected errors during token decoding
            # It's good to log this error on the server side for debugging
            # print(f"Unexpected error during token decoding: {e}") 
            return jsonify({'error': 'Erro interno ao processar token'}), 500
            
        return f(*args, **kwargs)
    return decorated

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Sub-task 2.1: Implement Professional Management Routes

@admin_bp.route('/professionals/pending', methods=['GET'])
@admin_required
def get_pending_professionals():
    try:
        pending_professionals = Professional.query.join(User, User.id == Professional.user_id)\
            .filter(Professional.approval_status == 'pending')\
            .add_columns(User.name, User.email, Professional.id, Professional.user_id, Professional.document_number, Professional.diploma_file, Professional.bio, Professional.created_at)\
            .all()
        
        results = []
        for prof_data in pending_professionals:
            results.append({
                "id": prof_data.id,
                "user_id": prof_data.user_id,
                "name": prof_data.name,
                "email": prof_data.email,
                "document_number": prof_data.document_number,
                "diploma_file": prof_data.diploma_file,
                "bio": prof_data.bio,
                "approval_status": 'pending', # Explicitly set as we filtered for it
                "created_at": prof_data.created_at.isoformat() if prof_data.created_at else None,
            })
        return jsonify(results), 200
    except Exception as e:
        # Log the error e
        return jsonify({"message": "Error fetching pending professionals", "error": str(e)}), 500

@admin_bp.route('/professionals/<int:prof_id>/approve', methods=['POST'])
@admin_required
def approve_professional(prof_id):
    try:
        professional = Professional.query.get(prof_id)
        if not professional:
            return jsonify({"message": "Professional not found"}), 404

        if professional.approval_status != 'pending':
            return jsonify({"message": f"Professional is already {professional.approval_status}"}), 400

        professional.approval_status = 'approved'
        professional.approval_date = datetime.utcnow()
        professional.rejection_reason = None 
        
        user = User.query.get(professional.user_id)
        if user:
            user.approval_status = 'approved' 
            user.updated_at = datetime.utcnow()
            db.session.add(user)

        db.session.add(professional)
        db.session.commit()
        return jsonify({"message": "Profissional aprovado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"message": "Error approving professional", "error": str(e)}), 500

@admin_bp.route('/professionals/<int:prof_id>/reject', methods=['POST'])
@admin_required
def reject_professional(prof_id):
    data = request.get_json()
    reason = data.get('reason', None) if data else None # Ensure data is not None

    try:
        professional = Professional.query.get(prof_id)
        if not professional:
            return jsonify({"message": "Professional not found"}), 404

        if professional.approval_status != 'pending':
            return jsonify({"message": f"Professional is already {professional.approval_status}"}), 400

        professional.approval_status = 'rejected'
        professional.rejection_reason = reason
        professional.approval_date = None 
        
        user = User.query.get(professional.user_id)
        if user:
            user.approval_status = 'rejected'
            user.updated_at = datetime.utcnow()
            db.session.add(user)
            
        db.session.add(professional)
        db.session.commit()
        return jsonify({"message": "Profissional rejeitado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"message": "Error rejecting professional", "error": str(e)}), 500

# Sub-task 2.2: Implement Activity Management Routes

@admin_bp.route('/activities', methods=['GET'])
@admin_required
def list_all_activities():
    try:
        activities = Activity.query.options(db.joinedload(Activity.category)).all()
        results = []
        for act in activities:
            category_info = None
            if act.category:
                category_info = {"id": act.category.id, "name": act.category.name}
            results.append({
                "id": act.id,
                "name": act.name,
                "description": act.description,
                "category_id": act.category_id,
                "category": category_info,
                # "created_at": act.created_at.isoformat() if act.created_at else None # Add if exists in model
            })
        return jsonify(results), 200
    except Exception as e:
        # Log the error e
        return jsonify({"message": "Error fetching activities", "error": str(e)}), 500

@admin_bp.route('/activities', methods=['POST'])
@admin_required
def add_activity():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid input"}), 400
        
    name = data.get('name')
    description = data.get('description')
    category_id = data.get('category_id')

    if not name or not name.strip():
        return jsonify({"message": "Activity name is required and cannot be empty"}), 400

    if category_id is not None: # category_id can be 0, so check for None
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"message": f"Category with id {category_id} not found"}), 400

    try:
        new_activity = Activity(
            name=name,
            description=description,
            category_id=category_id
        )
        db.session.add(new_activity)
        db.session.commit()
        
        category_info = None
        if new_activity.category_id is not None:
            cat = Category.query.get(new_activity.category_id) # Re-fetch to ensure fresh data
            if cat:
                 category_info = {"id": cat.id, "name": cat.name}
        
        return jsonify({
            "id": new_activity.id,
            "name": new_activity.name,
            "description": new_activity.description,
            "category_id": new_activity.category_id,
            "category": category_info,
            # "created_at": new_activity.created_at.isoformat() if new_activity.created_at else None # Add if exists
        }), 201
    except Exception as e: # Catch potential IntegrityError for unique name if not handled by DB
        db.session.rollback()
        # Log the error e
        if 'unique constraint' in str(e).lower(): # Basic check for unique constraint violation
            return jsonify({"message": f"Activity with name '{name}' already exists."}), 409
        return jsonify({"message": "Error adding activity", "error": str(e)}), 500

@admin_bp.route('/activities/<int:activity_id>', methods=['PUT'])
@admin_required
def update_activity(activity_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    try:
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({"message": "Activity not found"}), 404

        if 'name' in data:
            name = data['name']
            if not name or not name.strip():
                 return jsonify({"message": "Activity name cannot be empty"}), 400
            activity.name = name
        if 'description' in data:
            activity.description = data['description']
        if 'category_id' in data: # Allows setting category_id to null
            category_id = data['category_id']
            if category_id is not None:
                category = Category.query.get(category_id)
                if not category:
                    return jsonify({"message": f"Category with id {category_id} not found"}), 400
            activity.category_id = category_id
        
        # activity.updated_at = datetime.utcnow() # Add if Activity model has updated_at
        db.session.commit()

        category_info = None
        if activity.category_id is not None:
            cat = Category.query.get(activity.category_id)
            if cat:
                 category_info = {"id": cat.id, "name": cat.name}

        return jsonify({
            "id": activity.id,
            "name": activity.name,
            "description": activity.description,
            "category_id": activity.category_id,
            "category": category_info,
            # "updated_at": activity.updated_at.isoformat() # Add if model has updated_at
        }), 200
    except Exception as e:
        db.session.rollback()
        if 'unique constraint' in str(e).lower(): # Basic check for unique constraint violation
            return jsonify({"message": f"Activity with name '{data.get('name')}' already exists."}), 409
        # Log the error e
        return jsonify({"message": "Error updating activity", "error": str(e)}), 500

@admin_bp.route('/activities/<int:activity_id>', methods=['DELETE'])
@admin_required
def delete_activity(activity_id):
    try:
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({"message": "Activity not found"}), 404

        is_in_use = ProfessionalActivity.query.filter_by(activity_id=activity_id).first()
        if is_in_use:
            return jsonify({"message": "Activity is in use by a professional and cannot be deleted"}), 400

        db.session.delete(activity)
        db.session.commit()
        return jsonify({"message": "Activity deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"message": "Error deleting activity", "error": str(e)}), 500

# Ensure this blueprint is registered in app.py or main.py
# from src.routes.admin import admin_bp
# app.register_blueprint(admin_bp)
