from flask import Flask
from src.routes.auth import auth_bp
from src.routes.booking import booking_bp
from src.routes.patient import patient_bp
from src.routes.professional import professional_bp
from src.routes.search import search_bp
from src.routes.professional_activity import professional_activity_bp
from src.models.user import db
import os

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
app.register_blueprint(professional_activity_bp, url_prefix='/api/professional_activity')
app.register_blueprint(search_bp, url_prefix='/api/search')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
