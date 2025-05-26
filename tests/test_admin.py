import pytest
import jwt
from datetime import datetime, timedelta
from src.main import db # Corrected db import based on conftest.py
from src.models.user import User
from src.models.category import Category

# Removed local client fixture

def generate_admin_token(user_id, secret='test_secret_key_for_conftest'): # Ensure secret matches conftest
    payload = {
        'user_id': user_id,
        'user_type': 'admin',
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    # Ensure the secret used here matches the one in conftest.py or your app's config for testing
    return jwt.encode(payload, secret, algorithm='HS256')

@pytest.fixture
def admin_headers(client): # client fixture is from conftest.py
    with client.application.app_context(): # Use the application context from the client's app
        # For now, keep the existing user creation, but be mindful of plain text passwords
        # from werkzeug.security import generate_password_hash
        # hashed_password = generate_password_hash('123456')
        # admin = User(email='admin@example.com', password=hashed_password, name='Admin', user_type='admin')
        admin = User(email='admin@example.com', password='123456', name='Admin', user_type='admin')
        db.session.add(admin)
        db.session.commit()
        
        # Generate token using the admin user's ID
        token = generate_admin_token(admin.id) 
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            
        # The token needs to be returned by the fixture, but it's generated inside the context.
        # This is fine, the value will be returned after the context exits.
        auth_token = {'Authorization': f'Bearer {token}'}
    
    return auth_token

def test_get_pending_professionals(client, admin_headers):
    response = client.get('/api/admin/professionals/pending', headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_approve_professional(client, admin_headers):
    # Simular ID de profissional
    # This test will likely fail if professional with prof_id=1 doesn't exist.
    # Proper test setup would involve creating a professional first.
    prof_id = 1 
    response = client.post(f'/api/admin/professionals/{prof_id}/approve', headers=admin_headers)
    assert response.status_code == 200 # Or 404 if not found
    assert 'message' in response.get_json()

def test_reject_professional(client, admin_headers):
    prof_id = 2
    response = client.post(f'/api/admin/professionals/{prof_id}/reject', headers=admin_headers)
    assert response.status_code == 200 # Or 404 if not found
    assert 'message' in response.get_json()

def test_get_categories(client): # This test does not use admin_headers, so it's unaffected by its changes directly
    response = client.get('/api/admin/categories')
    assert response.status_code == 200 # This was failing with 404 previously
    assert isinstance(response.get_json(), list)

def test_add_category(client, admin_headers):
    response = client.post('/api/admin/categories', 
                           headers=admin_headers, 
                           json={'name': 'Fisioterapia', 'description': 'Atendimento fisioterápico'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Fisioterapia'

def test_update_category(client, admin_headers):
    # This test needs to ensure the category exists before trying to update it.
    # Create category within app_context for this test.
    with client.application.app_context():
        category = Category(name='Psicologia Original', description='Atendimento psicológico original')
        db.session.add(category)
        db.session.commit()
        category_id = category.id

    response = client.put(f'/api/admin/categories/{category_id}', 
                          headers=admin_headers, 
                          json={'name': 'Psicologia Atualizada'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Psicologia Atualizada'

    # Clean up or verify change in DB
    with client.application.app_context():
        updated_category = db.session.get(Category, category_id)
        assert updated_category is not None
        assert updated_category.name == 'Psicologia Atualizada'


def test_delete_category(client, admin_headers):
    # This test needs to ensure the category exists before trying to delete it.
    with client.application.app_context():
        category = Category(name='Enfermagem Para Deletar', description='Atendimento de enfermagem para deletar')
        db.session.add(category)
        db.session.commit()
        category_id = category.id
    
    response = client.delete(f'/api/admin/categories/{category_id}', headers=admin_headers)
    assert response.status_code == 200
    assert 'message' in response.get_json()

    # Verify deletion
    with client.application.app_context():
        deleted_category = db.session.get(Category, category_id)
        assert deleted_category is None
