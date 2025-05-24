
from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class ProfessionalActivity(db.Model):
    __tablename__ = 'professional_activities'
    id = db.Column(db.Integer, primary_key=True)
    activity_name = db.Column(db.String(100), nullable=False)
