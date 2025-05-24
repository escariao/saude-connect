
import json
from src.main import app, db
from src.models.professional_activity import ProfessionalActivity

def test_create_activity(client):
    response = client.post('/api/activities/', json={
        'professional_id': 1,
        'activity_name': 'Fisioterapia',
        'description': 'Atendimento domiciliar',
        'price': 150.0,
        'availability': 'Seg-Sex 08:00-18:00'
    })
    assert response.status_code == 201
    assert 'id' in response.get_json()

def test_list_activities(client):
    response = client.get('/api/activities/')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_activity(client):
    create_resp = client.post('/api/activities/', json={
        'professional_id': 1,
        'activity_name': 'Fonoaudiologia'
    })
    act_id = create_resp.get_json()['id']
    response = client.get(f'/api/activities/{act_id}')
    assert response.status_code == 200
    assert response.get_json()['activity_name'] == 'Fonoaudiologia'

def test_update_activity(client):
    create_resp = client.post('/api/activities/', json={
        'professional_id': 1,
        'activity_name': 'Acupuntura'
    })
    act_id = create_resp.get_json()['id']
    response = client.patch(f'/api/activities/{act_id}', json={'price': 200})
    assert response.status_code == 200

def test_delete_activity(client):
    create_resp = client.post('/api/activities/', json={
        'professional_id': 1,
        'activity_name': 'Pilates'
    })
    act_id = create_resp.get_json()['id']
    response = client.delete(f'/api/activities/{act_id}')
    assert response.status_code == 200
