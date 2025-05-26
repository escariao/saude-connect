import os
from flask import Flask, send_from_directory
from src.models.user import db  # db instance
from src.routes.auth import auth_bp
from src.routes.booking import booking_bp
from src.routes.patient import patient_bp
from src.routes.professional import professional_bp
from src.routes.professional_activity import professional_activity_bp
from src.routes.search import search_bp
from src.routes.user import user_bp

# Application Factory Function
def create_app(config_object=None):
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    # Configurations
    if config_object:
        app.config.from_object(config_object)
    else:
        # Default configurations if no config_object is provided
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///:memory:') # Default to in-memory for safety
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_change_me')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Add other default configs if necessary, e.g. app.config.from_envvar('YOURAPPLICATION_SETTINGS', silent=True)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(booking_bp, url_prefix='/api/booking')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(professional_bp, url_prefix='/api/professional')
    app.register_blueprint(professional_activity_bp, url_prefix='/api/professional_activity')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(user_bp, url_prefix='/api/user')

    # Main routes
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/<path:filename>')
    def serve_static(filename):
        # Ensure static_folder is correctly determined if create_app is called from elsewhere
        # For now, assuming __file__ context is appropriate.
        return send_from_directory(app.static_folder, filename)
    
    # Remove db.create_all() from here. It should be handled by migrations or test setup.
    # Example:
    # with app.app_context():
    #     db.create_all() # Only if you want it to run every time app is created and not using migrations

    return app

if __name__ == '__main__':
    app = create_app()  # Create app instance using the factory
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
