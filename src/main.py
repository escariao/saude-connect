from flask import Flask
from src.routes.auth import auth_bp
from src.routes.booking import booking_bp
from src.routes.patient import patient_bp
from src.routes.professional import professional_bp
from src.routes.search import search_bp
from src.routes.professional_activity import activity_bp
from src.models.user import db
import os

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuração do banco de dados
# Primeiro tenta usar DATABASE_URL do ambiente, se não existir, usa SQLite local
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Para compatibilidade com Render (PostgreSQL)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback para SQLite local (desenvolvimento)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saude_connect.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_for_testing')

db.init_app(app)

with app.app_context():
    db.create_all()

# Servir frontend na raiz
@app.route('/')
def index():
    return app.send_static_file('activities.html')

# Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(booking_bp, url_prefix='/api/booking')
app.register_blueprint(patient_bp, url_prefix='/api/patient')
app.register_blueprint(professional_bp, url_prefix='/api/professional')
app.register_blueprint(search_bp, url_prefix='/api/search')
app.register_blueprint(activity_bp, url_prefix='/api/activities')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
