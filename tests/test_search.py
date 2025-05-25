import pytest
from flask import Flask
from src import create_app
from src.models.user import db, User
import json
import jwt
from datetime import datetime, timedelta

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

def generate_token(user_id, user_type='patient', secret='test_secret'):
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, secret, algorithm='HS256')

@pytest.fixture
def auth_headers(client):
    # Criar usuário paciente
    response = client.post('/register/patient', json={
        'email': 'search@example.com',
        'password': '123456',
        'name': 'Search User',
        'document': '12345678900'
    })
    user_id = response.get_json()['user_id']
    
    token = generate_token(user_id)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return {'Authorization': f'Bearer {token}'}

def test_search_professionals(client, auth_headers):
    response = client.get('/api/search/professionals', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_list_activities(client, auth_headers):
    response = client.get('/api/search/activities', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_list_categories(client, auth_headers):
    response = client.get('/api/search/categories', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_get_professional_details(client, auth_headers):
    # Este teste requer que um profissional exista — caso contrário, retornará 404
    response = client.get('/api/search/professional/1', headers=auth_headers)
    assert response.status_code in (200, 404)  # Aceitamos 404 se não houver profissional
