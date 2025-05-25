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
    # Criar usuário
    response = client.post('/register/patient', json={
        'email': 'bookinguser@example.com',
        'password': '123456',
        'name': 'Booking User',
        'document': '12345678900'
    })
    user_id = response.get_json()['user_id']
    
    token = generate_token(user_id)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return {'Authorization': f'Bearer {token}'}

def test_create_booking(client, auth_headers):
    response = client.post('/api/booking/', 
        headers=auth_headers,
        json={
            'professional_id': 1,
            'scheduled_date': '2023-12-31T10:00:00',
            'status': 'pending'
        })
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data

def test_list_bookings(client, auth_headers):
    client.post('/api/booking/', 
        headers=auth_headers,
        json={
            'professional_id': 1,
            'scheduled_date': '2023-12-31T10:00:00',
            'status': 'pending'
        })
    
    response = client.get('/api/booking/', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_get_booking(client, auth_headers):
    create_response = client.post('/api/booking/', 
        headers=auth_headers,
        json={
            'professional_id': 1,
            'scheduled_date': '2023-12-31T10:00:00',
            'status': 'pending'
        })
    booking_id = create_response.get_json()['id']
    
    response = client.get(f'/api/booking/{booking_id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == booking_id

def test_update_booking(client, auth_headers):
    create_response = client.post('/api/booking/', 
        headers=auth_headers,
        json={
            'professional_id': 1,
            'scheduled_date': '2023-12-31T10:00:00',
            'status': 'pending'
        })
    booking_id = create_response.get_json()['id']
    
    response = client.put(f'/api/booking/{booking_id}', 
        headers=auth_headers,
        json={'status': 'confirmed'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'confirmed'

def test_delete_booking(client, auth_headers):
    create_response = client.post('/api/booking/', 
        headers=auth_headers,
        json={
            'professional_id': 1,
            'scheduled_date': '2023-12-31T10:00:00',
            'status': 'pending'
        })
    booking_id = create_response.get_json()['id']
    
    response = client.delete(f'/api/booking/{booking_id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
