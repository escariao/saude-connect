import os
from flask import Flask, send_from_directory

# Configuração da aplicação Flask
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Importação dos blueprints
from src.routes.auth import auth_bp
from src.routes.booking import booking_bp
from src.routes.patient import patient_bp
from src.routes.professional import professional_bp
from src.routes.professional_activity import professional_activity_bp
from src.routes.search import search_bp
from src.routes.user import user_bp
from src.routes.admin import admin_bp
from src.models.user import db

# Configuração do banco de dados
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_change_me')

# Inicialização do banco de dados
db.init_app(app)

# Registro dos blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(booking_bp, url_prefix='/api/booking')
app.register_blueprint(patient_bp, url_prefix='/api/patient')
app.register_blueprint(professional_bp, url_prefix='/api/professional')
app.register_blueprint(professional_activity_bp, url_prefix='/api/professional_activity')
app.register_blueprint(search_bp, url_prefix='/api/search')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Rotas principais
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# Criação das tabelas do banco de dados
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
