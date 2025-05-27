import pytest
# Removed Flask and create_app imports
from src.main import db # Corrected db import
from src.models.user import User
from src.models.professional_activity import ProfessionalActivity # Added ProfessionalActivity model import
import json
import jwt
from datetime import datetime, timedelta
from flask import current_app # To access app config for SECRET_KEY
import io # For file stub

# Removed local client fixture

def generate_token(user_id, user_type='professional'): # Removed hardcoded secret
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    secret = current_app.config.get('SECRET_KEY', 'test_secret_key_for_conftest')
    return jwt.encode(payload, secret, algorithm='HS256')

@pytest.fixture
def auth_headers(client): # client is from conftest.py
    # Criar usuário profissional
    # Note: Professional registration requires multipart/form-data with a file.
    # This fixture will likely need adjustment for a fully passing test.
    # For now, focusing on path and basic setup.
    form_data = {
        'email': 'prof@example.com',
        'password': '123456',
        'name': 'Professional User',
        'document': '12345678900',
        'registration_number': 'CRM12345',
        'specialty': 'Cardiology',
        'professional_type': 'doctor', # Assuming 'doctor' or similar valid type
        'curriculum_vitae': (io.BytesIO(b"dummy cv content"), 'cv.pdf')
    }
    response = client.post('/api/auth/register/professional', data=form_data, content_type='multipart/form-data') # Updated URL
    
    user_data = response.get_json()
    if response.status_code != 201:
        # Attempt to query user if registration failed but user might exist from previous run or setup
        user = User.query.filter_by(email='prof@example.com').first()
        if not user:
            raise Exception(f"Failed to register professional user: {response.status_code} {user_data.get('message') or user_data.get('error')}")
        user_id = user.id
    else:
        user_id = user_data['user_id']
    
    token = generate_token(user_id)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return {'Authorization': f'Bearer {token}'}

def test_list_professional_activities(client): # auth_headers not strictly needed if endpoint is public
    response = client.get('/api/professional_activity/') # Path is correct
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_create_professional_activity(client, auth_headers):
    response = client.post('/api/professional_activity/', # Path is correct
        headers=auth_headers,
        json={
            'name': 'Consulta', # Ensure this professional has this activity type or adjust
            'description': 'Atendimento presencial',
            'price': 100.0,
            'years_of_experience': 5 # Ensure this aligns with professional's experience if validated
        })
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data

def test_get_professional_activity(client, auth_headers): # auth_headers might not be needed if public
    # Create a professional activity to get
    create_response = client.post('/api/professional_activity/', 
        headers=auth_headers, # Assuming creation needs auth
        json={
            'name': 'Teleconsulta', # Using a potentially different name for clarity
            'description': 'Atendimento online',
            'price': 80.0,
            'years_of_experience': 3
        })
    assert create_response.status_code == 201 # Ensure creation was successful
    activity_id = create_response.get_json()['id']
    
    response = client.get(f'/api/professional_activity/{activity_id}') # Path is correct
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == activity_id
