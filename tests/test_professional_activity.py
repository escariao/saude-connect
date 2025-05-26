import pytest
# Removed Flask and create_app imports
from src.main import db # Corrected db import
from src.models.user import User
from src.models.professional_activity import ProfessionalActivity
from src.models.professional import Activity # Changed back to absolute import
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
        'phone': '0987654321',  # Added phone
        'bio': 'A brief bio for the professional.', # Added bio
        # Removed registration_number, specialty, professional_type
        'diploma': (io.BytesIO(b"dummy diploma content"), 'diploma.pdf') # Corrected key and content
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
    # Create a prerequisite Activity for the test
    with client.application.app_context():
        test_activity = Activity(name="Test General Activity", description="An activity for testing")
        db.session.add(test_activity)
        db.session.commit()
        activity_id_to_use = test_activity.id

    response = client.post('/api/professional_activity/', 
        headers=auth_headers,
        json={
            'activity_id': activity_id_to_use, # Use the ID of the created Activity
            'description': 'Atendimento presencial de teste',
            'price': 120.0,
            'availability': 'Mon-Fri, 9am-5pm'
        })
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
    assert data['activity_id'] == activity_id_to_use

def test_get_professional_activity(client, auth_headers):
    with client.application.app_context():
        test_activity_for_get = Activity(name="Test Activity For Get", description="Another activity for testing get")
        db.session.add(test_activity_for_get)
        db.session.commit()
        activity_id_for_prof_act = test_activity_for_get.id

    create_response = client.post('/api/professional_activity/', 
        headers=auth_headers,
        json={
            'activity_id': activity_id_for_prof_act,
            'description': 'Atendimento online de teste para GET',
            'price': 90.0,
            'availability': 'Weekends'
        })
    assert create_response.status_code == 201
    created_prof_activity_data = create_response.get_json()
    prof_activity_id_to_get = created_prof_activity_data['id']
    
    response = client.get(f'/api/professional_activity/{prof_activity_id_to_get}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == prof_activity_id_to_get
    assert data['activity_id'] == activity_id_for_prof_act
