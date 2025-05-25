import pytest
from flask import Flask
from src import create_app  # Ajuste conforme como você instancia a app
from src.models.user import db, User
import json

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_register_patient_success(client):
    response = client.post('/register/patient', json={
        'email': 'test@example.com',
        'password': '123456',
        'name': 'Test User',
        'document': '12345678900'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'user_id' in data

def test_register_patient_missing_fields(client):
    response = client.post('/register/patient', json={
        'email': 'test@example.com'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_register_patient_duplicate_email(client):
    client.post('/register/patient', json={
        'email': 'test@example.com',
        'password': '123456',
        'name': 'Test User',
        'document': '12345678900'
    })
    
    response = client.post('/register/patient', json={
        'email': 'test@example.com',
        'password': '123456',
        'name': 'Test User',
        'document': '12345678900'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_login_success(client):
    # Primeiro, criar usuário
    client.post('/register/patient', json={
        'email': 'login@example.com',
        'password': '123456',
        'name': 'Login User',
        'document': '12345678900'
    })

    response = client.post('/login', json={
        'email': 'login@example.com',
        'password': '123456'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data

def test_login_incorrect_password(client):
    client.post('/register/patient', json={
        'email': 'loginfail@example.com',
        'password': '123456',
        'name': 'Login Fail',
        'document': '12345678900'
    })

    response = client.post('/login', json={
        'email': 'loginfail@example.com',
        'password': 'wrongpass'
    })
    assert response.status_code == 401
    data = response.get_json()
    assert 'message' in data

def test_login_missing_fields(client):
    response = client.post('/login', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
