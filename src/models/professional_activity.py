from src.models.user import db

class ProfessionalActivity(db.Model):
    __tablename__ = 'professional_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    # activity_name = db.Column(db.String(100), nullable=False) # Removed
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False) # Added ForeignKey
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    availability = db.Column(db.String(255))  # Pode ser melhorado no futuro para JSON se necessário

    def serialize(self):
        # Accessing activity.name would require a join, which might not be efficient here.
        # Or, load it explicitly when querying ProfessionalActivity if activity_name is needed.
        # For now, returning activity_id.
        return {
            'id': self.id,
            'professional_id': self.professional_id,
            'activity_id': self.activity_id, # Changed from activity_name
            # 'activity_name': self.activity.name if self.activity else None, # Example if relationship is eager/loaded
            'description': self.description,
            'price': self.price,
            'availability': self.availability
        }

    def __repr__(self):
        return f"<ProfessionalActivity {self.id} - activity_id:{self.activity_id}>" # Changed
