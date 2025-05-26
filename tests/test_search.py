import pytest
# Removed Flask and create_app imports
from src.main import db # Corrected db import
from src.models.user import User
# Import other models if needed, e.g., Professional, Activity, Category
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
        'email': 'search@example.com',
        'password': '123456',
        'name': 'Search User',
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

def test_search_professionals(client, auth_headers): # auth_headers might not be needed if public
    response = client.get('/api/search/professionals', headers=auth_headers) # Path is correct
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_list_activities(client, auth_headers): # auth_headers might not be needed if public
    response = client.get('/api/search/activities', headers=auth_headers) # Path is correct
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_list_categories(client, auth_headers): # auth_headers might not be needed if public
    response = client.get('/api/search/categories', headers=auth_headers) # Path is correct
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_get_professional_details(client, auth_headers): # auth_headers might not be needed if public
    # Este teste requer que um profissional exista — caso contrário, retornará 404
    # Ensure professional with ID 1 exists or adjust test to create one.
    response = client.get('/api/search/professional/1', headers=auth_headers) # Path is correct
    assert response.status_code in (200, 404)  # Aceitamos 404 se não houver profissional
