import pytest
# Removed Flask and create_app imports
from src.main import db # Corrected db import
from src.models.user import User
from src.models.patient import Patient # Added Patient model import
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
    secret = current_app.config.get('SECRET_KEY', 'test_secret_key_for_conftest')
    return jwt.encode(payload, secret, algorithm='HS256')

@pytest.fixture
def auth_headers(client): # client is from conftest.py
    # Criar usuário paciente
    response = client.post('/api/auth/register/patient', json={ # Updated URL
        'email': 'patient@example.com',
        'password': '123456',
        'name': 'Patient User',
        'document': '12345678900',
        'phone': '1234567890' # Added phone
    })
    user_data = response.get_json()
    if response.status_code != 201:
        raise Exception(f"Failed to register user for auth_headers: {response.status_code} {user_data.get('message') or user_data.get('error')}")
    user_id = user_data['user_id']
    
    token = generate_token(user_id)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return {'Authorization': f'Bearer {token}'}, user_id

def test_create_patient(client, auth_headers):
    headers, user_id = auth_headers # user_id from registered patient
    response = client.post(f'/api/patient/', # Updated URL
        headers=headers,
        json={'phone': '11999999999', 'user_id': user_id} # Ensure user_id is passed if required by endpoint
    )
    
    # Assuming 201 for successful creation. If API updates patient, 200 might be ok.
    assert response.status_code == 201 
    data = response.get_json()
    assert 'id' in data # Patient model ID

def test_get_patient(client, auth_headers):
    headers, user_id = auth_headers
    # Create the patient profile first
    client.post(f'/api/patient/', headers=headers, json={'phone': '11999999999', 'user_id': user_id})
    
    response = client.get(f'/api/patient/{user_id}', headers=headers) # Updated URL
    assert response.status_code == 200
    data = response.get_json()
    assert data['user_id'] == user_id
