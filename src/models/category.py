from src.models.user import db

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True) # Added description field

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description # Added description to dictionary
        }
