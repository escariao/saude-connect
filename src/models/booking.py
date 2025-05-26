# Removed flask_sqlalchemy import as db is imported from user
from datetime import datetime
from .user import db # Changed to relative import

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pendente')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'

    def serialize(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'professional_id': self.professional_id,
            'date_time': self.date_time.isoformat() if self.date_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
