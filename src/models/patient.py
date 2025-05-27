from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
from datetime import datetime

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document = db.Column(db.String(50), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)  # Alterado para nullable=True para compatibilidade
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Patient {self.id}>'
        
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'document': self.document,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
