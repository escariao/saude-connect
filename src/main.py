import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.models.user import db, User
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.patient import patient_bp
from src.routes.admin import admin_bp
from src.routes.search import search_bp
from src.routes.booking import booking_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(patient_bp, url_prefix='/api/patient')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(search_bp, url_prefix='/api/search')
app.register_blueprint(booking_bp, url_prefix='/api/booking')

# Configuração do banco de dados
database_url = os.getenv('DATABASE_URL')

if database_url:
    # Configuração para Render (PostgreSQL)
    # Render fornece URLs no formato: postgres://user:password@host:port/dbname
    # SQLAlchemy espera: postgresql://user:password@host:port/dbname
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Configuração para desenvolvimento local (MySQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Configuração para upload de arquivos
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'public', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Criar tabelas do banco de dados
with app.app_context():
    db.create_all()
    
    # Verificar se já existe um usuário admin
    admin = User.query.filter_by(user_type='admin').first()
    if not admin:
        # Criar usuário admin padrão
        from werkzeug.security import generate_password_hash
        admin = User(
            email='admin@saudeconnect.com',
            password=generate_password_hash('admin123'),
            name='Administrador',
            user_type='admin'
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
