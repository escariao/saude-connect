import pytest
# Removed Flask and create_app imports
from src.main import db # Corrected db import
from src.models.user import User # Assuming User model is still relevant
from src.models.booking import Booking # Added Booking model import based on usage
import json
import jwt
from datetime import datetime, timedelta
from flask import current_app # To access app config for SECRET_KEY

# Removed local client fixture

def generate_token(user_id, user_type='patient'): # Removed hardcoded secret
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    # Use SECRET_KEY from app config, ensuring consistency
    secret = current_app.config.get('SECRET_KEY', 'test_secret_key_for_conftest')
    return jwt.encode(payload, secret, algorithm='HS256')

@pytest.fixture
def auth_headers(client): # client is from conftest.py
    # Criar usuário
    # Ensure db session is active if User creation hits db before request
    # This might be handled by app_context in conftest client
    response = client.post('/api/auth/register/patient', json={ # Updated URL
        'email': 'bookinguser@example.com',
        'password': '123456',
        'name': 'Booking User',
        'document': '12345678900'
    })
    user_data = response.get_json()
    if response.status_code != 201:
        raise Exception(f"Failed to register user for auth_headers: {response.status_code} {user_data.get('message') or user_data.get('error')}")
    user_id = user_data['user_id']
    
    token = generate_token(user_id)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return {'Authorization': f'Bearer {token}'}

def test_create_booking(client, auth_headers):
    # Ensure a professional user exists for professional_id = 1, or adjust test data
    # For now, assuming professional_id=1 is valid or will be handled by other test setups.
    response = client.post('/api/booking/', 
        headers=auth_headers,
        json={
            'professional_id': 1, # This professional needs to exist
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
