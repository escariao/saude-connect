import pytest
import jwt
from datetime import datetime, timedelta
from src import create_app
from src.models.user import db, User
from src.models.category import Category

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def generate_admin_token(user_id, secret='test_secret'):
    payload = {
        'user_id': user_id,
        'user_type': 'admin',
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, secret, algorithm='HS256')

@pytest.fixture
def admin_headers(client):
    admin = User(email='admin@example.com', password='123456', name='Admin', user_type='admin')
    db.session.add(admin)
    db.session.commit()
    
    token = generate_admin_token(admin.id)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
        
    return {'Authorization': f'Bearer {token}'}

def test_get_pending_professionals(client, admin_headers):
    response = client.get('/api/admin/professionals/pending', headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_approve_professional(client, admin_headers):
    # Simular ID de profissional
    prof_id = 1
    response = client.post(f'/api/admin/professionals/{prof_id}/approve', headers=admin_headers)
    assert response.status_code == 200
    assert 'message' in response.get_json()

def test_reject_professional(client, admin_headers):
    prof_id = 2
    response = client.post(f'/api/admin/professionals/{prof_id}/reject', headers=admin_headers)
    assert response.status_code == 200
    assert 'message' in response.get_json()

def test_get_categories(client):
    response = client.get('/api/admin/categories')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_add_category(client, admin_headers):
    response = client.post('/api/admin/categories', 
                           headers=admin_headers, 
                           json={'name': 'Fisioterapia', 'description': 'Atendimento fisioterápico'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Fisioterapia'

def test_update_category(client, admin_headers):
    category = Category(name='Psicologia', description='Atendimento psicológico')
    db.session.add(category)
    db.session.commit()
    
    response = client.put(f'/api/admin/categories/{category.id}', 
                          headers=admin_headers, 
                          json={'name': 'Psicologia Atualizada'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Psicologia Atualizada'

def test_delete_category(client, admin_headers):
    category = Category(name='Enfermagem', description='Atendimento de enfermagem')
    db.session.add(category)
    db.session.commit()
    
    response = client.delete(f'/api/admin/categories/{category.id}', headers=admin_headers)
    assert response.status_code == 200
    assert 'message' in response.get_json()
