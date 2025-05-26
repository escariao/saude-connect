# tests/conftest.py

import pytest
from src.main import create_app # Import the application factory
from src.models.user import db # Import the SQLAlchemy db instance

@pytest.fixture
def client():
    # Create an app instance using the factory
    # We can pass a specific test config object/name if create_app supports it.
    # For now, we'll configure it after creation.
    app = create_app() 

    # Apply test-specific configurations
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key_for_conftest' # Consistent test secret key
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for tests if Flask-WTF is used

    with app.test_client() as client:
        with app.app_context():
            db.create_all() # Create database tables for tests
        yield client
        with app.app_context():
            db.drop_all() # Drop database tables after tests
