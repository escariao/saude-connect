import os
from flask import Flask
from src.models.user import db
from src.routes.auth import auth_bp
from src.routes.booking import booking_bp
from src.routes.patient import patient_bp
from src.routes.professional import professional_bp
from src.routes.professional_activity import professional_activity_bp
from src.routes.search import search_bp
from src.routes.user import user_bp  # Adicionado!

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')

# Inicialização do banco
db.init_app(app)

with app.app_context():
    db.create_all()

# Rotas principais
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Registro de Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(booking_bp, url_prefix='/api/booking')
app.register_blueprint(patient_bp, url_prefix='/api/patient')
app.register_blueprint(professional_bp, url_prefix='/api/professional')
app.register_blueprint(professional_activity_bp, url_prefix='/api/professional_activity')
app.register_blueprint(search_bp, url_prefix='/api/search')
app.register_blueprint(user_bp, url_prefix='/api/user')  # Agora está registrado!

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
