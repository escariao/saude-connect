from src.models.user import db

class ProfessionalActivity(db.Model):
    __tablename__ = 'professional_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    activity_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    availability = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'professional_id': self.professional_id,
            'activity_name': self.activity_name,
            'description': self.description,
            'price': self.price,
            'availability': self.availability
        }
