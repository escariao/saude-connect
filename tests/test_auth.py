import pytest
# Removed Flask import as create_app is no longer used here
# from src import create_app # Removed local create_app import
from src.main import db # Corrected db import based on conftest.py
from src.models.user import User
import json

# Removed local client fixture, conftest.py client will be used

def test_register_patient_success(client): # client is now from conftest.py
    response = client.post('/api/auth/register/patient', json={ # Updated URL
        'email': 'test@example.com',
        'password': '123456',
        'name': 'Test User',
        'document': '12345678900'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'user_id' in data

def test_register_patient_missing_fields(client):
    response = client.post('/api/auth/register/patient', json={ # Updated URL
        'email': 'test@example.com'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_register_patient_duplicate_email(client):
    client.post('/api/auth/register/patient', json={ # Updated URL
        'email': 'test@example.com',
        'password': '123456',
        'name': 'Test User',
        'document': '12345678900'
    })
    
    response = client.post('/api/auth/register/patient', json={ # Updated URL
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
    client.post('/api/auth/register/patient', json={ # Updated URL
        'email': 'login@example.com',
        'password': '123456',
        'name': 'Login User',
        'document': '12345678900'
    })

    response = client.post('/api/auth/login', json={ # Updated URL
        'email': 'login@example.com',
        'password': '123456'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data

def test_login_incorrect_password(client):
    client.post('/api/auth/register/patient', json={ # Updated URL
        'email': 'loginfail@example.com',
        'password': '123456',
        'name': 'Login Fail',
        'document': '12345678900'
    })

    response = client.post('/api/auth/login', json={ # Updated URL
        'email': 'loginfail@example.com',
        'password': 'wrongpass'
    })
    assert response.status_code == 401
    data = response.get_json()
    assert 'message' in data

def test_login_missing_fields(client):
    response = client.post('/api/auth/login', json={}) # Updated URL
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
