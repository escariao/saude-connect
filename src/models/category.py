from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class ProfessionalActivity(db.Model):
    __tablename__ = 'professional_activities'
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    activity_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    availability = db.Column(db.String(255))
