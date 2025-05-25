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

def generate_token(user_id, user_type='professional', secret='test_secret'):
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, secret, algorithm='HS256')

@pytest.fixture
def auth_headers(client):
    # Criar usuário profissional
    response = client.post('/register/professional', data={
        'email': 'prof@example.com',
        'password': '123456',
        'name': 'Professional User',
        'document': '12345678900'
    })
    user_id = User.query.filter_by(email='prof@example.com').first().id
    
    token = generate_token(user_id)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return {'Authorization': f'Bearer {token}'}

def test_list_professional_activities(client):
    response = client.get('/api/professional_activity/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_create_professional_activity(client, auth_headers):
    response = client.post('/api/professional_activity/', 
        headers=auth_headers,
        json={
            'name': 'Consulta',
            'description': 'Atendimento presencial',
            'price': 100.0,
            'years_of_experience': 5
        })
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data

def test_get_professional_activity(client, auth_headers):
    create_response = client.post('/api/professional_activity/', 
        headers=auth_headers,
        json={
            'name': 'Consulta',
            'description': 'Atendimento presencial',
            'price': 100.0,
            'years_of_experience': 5
        })
    activity_id = create_response.get_json()['id']
    
    response = client.get(f'/api/professional_activity/{activity_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == activity_id
