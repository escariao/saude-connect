from src.models.user import db

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relacionamento com atividades - corrigido para usar backref
    activities = db.relationship('Activity', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'
