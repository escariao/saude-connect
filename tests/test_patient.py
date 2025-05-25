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
        'email': 'patient@example.com',
        'password': '123456',
        'name': 'Patient User',
        'document': '12345678900'
    })
    user_id = response.get_json()['user_id']
    
    token = generate_token(user_id)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return {'Authorization': f'Bearer {token}'}, user_id

def test_create_patient(client, auth_headers):
    headers, _ = auth_headers
    response = client.post('/patient/', 
        headers=headers,
        json={'phone': '11999999999'})
    
    assert response.status_code == 201 or response.status_code == 200  # dependendo da implementação
    data = response.get_json()
    assert 'id' in data or 'message' in data

def test_get_patient(client, auth_headers):
    headers, user_id = auth_headers
    # Primeiro criar o perfil de paciente
    client.post('/patient/', headers=headers, json={'phone': '11999999999'})
    
    response = client.get(f'/patient/{user_id}', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['user_id'] == user_id
