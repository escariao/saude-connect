
from .user import db # Changed to relative import
from .professional_activity import ProfessionalActivity # Changed to relative import
from datetime import datetime

class Professional(db.Model):
    __tablename__ = 'professionals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_number = db.Column(db.String(20), nullable=False)  # CPF ou documento profissional
    diploma_file = db.Column(db.String(255), nullable=False)  # Caminho para o arquivo do diploma
    bio = db.Column(db.Text, nullable=True)
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approval_date = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com atividades/especialidades
    activities = db.relationship('ProfessionalActivity', backref='professional', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Professional {self.id}>'


class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    # Substituindo o campo de texto por uma chave estrangeira
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com profissionais
    professionals = db.relationship('ProfessionalActivity', backref='activity')
    
    def __repr__(self):
        return f'<Activity {self.name}>'
