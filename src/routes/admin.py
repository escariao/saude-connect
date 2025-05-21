from flask import Blueprint, request, jsonify, current_app, send_from_directory
import os
from functools import wraps

from src.models.user import db, User
from src.models.professional import Professional, Activity, ProfessionalActivity
from src.routes.user import token_required

admin_bp = Blueprint('admin', __name__)

# Função para verificar se o usuário é administrador
def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.user_type != 'admin':
            return jsonify({'error': 'Acesso restrito a administradores'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

# Listar profissionais pendentes de aprovação
@admin_bp.route('/professionals/pending', methods=['GET'])
@token_required
@admin_required
def get_pending_professionals(current_user):
    pending_professionals = Professional.query.filter_by(approval_status='pending').all()
    
    result = []
    for prof in pending_professionals:
        user = User.query.get(prof.user_id)
        if user:
            result.append({
                'id': prof.id,
                'user_id': prof.user_id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'document_number': prof.document_number,
                'bio': prof.bio,
                'diploma_file': prof.diploma_file,
                'created_at': prof.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'activities': [{
                    'id': pa.id,
                    'activity_name': pa.activity.name,
                    'description': pa.description,
                    'experience_years': pa.experience_years,
                    'price': pa.price
                } for pa in prof.activities]
            })
    
    return jsonify(result), 200

# Aprovar um profissional
@admin_bp.route('/professionals/<int:prof_id>/approve', methods=['POST'])
@token_required
@admin_required
def approve_professional(current_user, prof_id):
    professional = Professional.query.get(prof_id)
    
    if not professional:
        return jsonify({'error': 'Profissional não encontrado'}), 404
        
    if professional.approval_status != 'pending':
        return jsonify({'error': 'Este profissional já foi processado'}), 400
        
    professional.approval_status = 'approved'
    professional.approval_date = db.func.now()
    
    db.session.commit()
    
    return jsonify({'message': 'Profissional aprovado com sucesso'}), 200

# Rejeitar um profissional
@admin_bp.route('/professionals/<int:prof_id>/reject', methods=['POST'])
@token_required
@admin_required
def reject_professional(current_user, prof_id):
    data = request.get_json()
    reason = data.get('reason', 'Não especificado')
    
    professional = Professional.query.get(prof_id)
    
    if not professional:
        return jsonify({'error': 'Profissional não encontrado'}), 404
        
    if professional.approval_status != 'pending':
        return jsonify({'error': 'Este profissional já foi processado'}), 400
        
    professional.approval_status = 'rejected'
    professional.rejection_reason = reason
    
    db.session.commit()
    
    return jsonify({'message': 'Profissional rejeitado com sucesso'}), 200

# Visualizar diploma de um profissional
@admin_bp.route('/professionals/<int:prof_id>/diploma', methods=['GET'])
@token_required
@admin_required
def view_diploma(current_user, prof_id):
    professional = Professional.query.get(prof_id)
    
    if not professional or not professional.diploma_file:
        return jsonify({'error': 'Diploma não encontrado'}), 404
        
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, professional.diploma_file)

# Gerenciar atividades/especialidades
@admin_bp.route('/activities', methods=['GET'])
@token_required
@admin_required
def get_all_activities(current_user):
    activities = Activity.query.all()
    return jsonify([{
        'id': activity.id,
        'name': activity.name,
        'description': activity.description,
        'category': activity.category
    } for activity in activities]), 200

@admin_bp.route('/activities', methods=['POST'])
@token_required
@admin_required
def create_activity(current_user):
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Nome da atividade é obrigatório'}), 400
        
    # Verificar se a atividade já existe
    if Activity.query.filter_by(name=data.get('name')).first():
        return jsonify({'error': 'Atividade já cadastrada'}), 400
        
    new_activity = Activity(
        name=data.get('name'),
        description=data.get('description'),
        category=data.get('category')
    )
    
    db.session.add(new_activity)
    db.session.commit()
    
    return jsonify({
        'message': 'Atividade cadastrada com sucesso',
        'activity': {
            'id': new_activity.id,
            'name': new_activity.name,
            'description': new_activity.description,
            'category': new_activity.category
        }
    }), 201
