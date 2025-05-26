import pytest
from flask import current_app
from src.models.user import User, db
from src.models.professional import Professional

@pytest.fixture(scope='module')
def test_data_professional_profile(app_context):
    with app_context:
        # Admin User for testing admin updates
        admin_user = User.query.filter_by(email='admin_prof_profile@test.com').first()
        if not admin_user:
            admin_user = User(email='admin_prof_profile@test.com', password=current_app.config['TEST_USER_PASSWORD'], name='Admin ProfProfile', user_type='admin', approval_status='approved')
            db.session.add(admin_user)

        # Professional User 1 (for self-update)
        prof_user1 = User.query.filter_by(email='prof1_profile@test.com').first()
        if not prof_user1:
            prof_user1 = User(email='prof1_profile@test.com', password=current_app.config['TEST_USER_PASSWORD'], name='Prof1 Profile', user_type='professional', approval_status='approved')
            db.session.add(prof_user1)
        
        # Professional User 2 (for admin to update, and to test unauthorized update by prof1)
        prof_user2 = User.query.filter_by(email='prof2_profile@test.com').first()
        if not prof_user2:
            prof_user2 = User(email='prof2_profile@test.com', password=current_app.config['TEST_USER_PASSWORD'], name='Prof2 Profile', user_type='professional', approval_status='pending') # Starts as pending
            db.session.add(prof_user2)

        db.session.flush()

        professional1 = Professional.query.filter_by(user_id=prof_user1.id).first()
        if not professional1:
            professional1 = Professional(user_id=prof_user1.id, document_number='PROF1P', diploma_file='prof1p.pdf', bio='Initial Bio Prof1', approval_status='approved')
            db.session.add(professional1)

        professional2 = Professional.query.filter_by(user_id=prof_user2.id).first()
        if not professional2:
            professional2 = Professional(user_id=prof_user2.id, document_number='PROF2P', diploma_file='prof2p.pdf', bio='Initial Bio Prof2', approval_status='pending') # Matches user
            db.session.add(professional2)
        
        db.session.commit()
        return {
            "admin_user_id": admin_user.id,
            "prof_user1_id": prof_user1.id,
            "professional1_id": professional1.id,
            "prof_user2_id": prof_user2.id,
            "professional2_id": professional2.id,
        }

@pytest.fixture(scope='module')
def auth_headers_professional_profile(client, test_data_professional_profile):
    # Admin Login
    admin_login_res = client.post('/api/auth/login', json={'email': 'admin_prof_profile@test.com', 'password': current_app.config['TEST_USER_PASSWORD']})
    admin_token = admin_login_res.json['token']
    
    # Prof1 Login
    prof1_login_res = client.post('/api/auth/login', json={'email': 'prof1_profile@test.com', 'password': current_app.config['TEST_USER_PASSWORD']})
    prof1_token = prof1_login_res.json['token']
        
    return {
        'admin': {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'},
        'prof1': {'Authorization': f'Bearer {prof1_token}', 'Content-Type': 'application/json'},
    }

# --- Professional Profile Update Tests ---

def test_professional_updates_own_bio(client, auth_headers_professional_profile, test_data_professional_profile):
    prof1_id = test_data_professional_profile['professional1_id']
    new_bio = "Updated bio by professional himself."
    response = client.put(f'/api/professional/{prof1_id}', headers=auth_headers_professional_profile['prof1'], json={
        'bio': new_bio
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Profissional atualizado com sucesso!'
    
    updated_prof = Professional.query.get(prof1_id)
    assert updated_prof.bio == new_bio

def test_professional_attempts_to_update_own_approval_status(client, auth_headers_professional_profile, test_data_professional_profile):
    prof1_id = test_data_professional_profile['professional1_id']
    response = client.put(f'/api/professional/{prof1_id}', headers=auth_headers_professional_profile['prof1'], json={
        'approval_status': 'rejected' # Attempt to change status
    })
    assert response.status_code == 403
    assert response.json['error'] == 'Você não tem permissão para alterar o status de aprovação.'

def test_admin_updates_professional_bio(client, auth_headers_professional_profile, test_data_professional_profile):
    prof2_id = test_data_professional_profile['professional2_id']
    new_bio_by_admin = "Admin updated this bio."
    response = client.put(f'/api/professional/{prof2_id}', headers=auth_headers_professional_profile['admin'], json={
        'bio': new_bio_by_admin
    })
    assert response.status_code == 200
    updated_prof = Professional.query.get(prof2_id)
    assert updated_prof.bio == new_bio_by_admin

def test_admin_updates_professional_approval_status(client, auth_headers_professional_profile, test_data_professional_profile):
    prof2_id = test_data_professional_profile['professional2_id']
    prof2_user_id = test_data_professional_profile['prof_user2_id']

    # Initial check (optional, but good for sanity)
    prof_before = Professional.query.get(prof2_id)
    assert prof_before.approval_status == 'pending'
    user_before = User.query.get(prof2_user_id)
    assert user_before.approval_status == 'pending'


    response = client.put(f'/api/professional/{prof2_id}', headers=auth_headers_professional_profile['admin'], json={
        'approval_status': 'approved'
    })
    assert response.status_code == 200
    
    updated_prof = Professional.query.get(prof2_id)
    assert updated_prof.approval_status == 'approved'
    # Note: The /api/professional/<id> PUT route might not update User.approval_status.
    # This was handled in /admin/professionals/<id>/approve.
    # If this route should also update User.approval_status, the route logic needs adjustment.
    # For now, we only test what Professional.approval_status is set to.

def test_admin_updates_professional_bio_and_status(client, auth_headers_professional_profile, test_data_professional_profile):
    prof2_id = test_data_professional_profile['professional2_id']
    new_bio = "Bio and status update by admin."
    new_status = "rejected" # Change from pending/approved to rejected
    
    response = client.put(f'/api/professional/{prof2_id}', headers=auth_headers_professional_profile['admin'], json={
        'bio': new_bio,
        'approval_status': new_status
    })
    assert response.status_code == 200
    
    updated_prof = Professional.query.get(prof2_id)
    assert updated_prof.bio == new_bio
    assert updated_prof.approval_status == new_status

def test_professional_attempts_to_update_another_professionals_profile(client, auth_headers_professional_profile, test_data_professional_profile):
    prof2_id = test_data_professional_profile['professional2_id'] # Target prof2
    response = client.put(f'/api/professional/{prof2_id}', headers=auth_headers_professional_profile['prof1'], json={ # Using prof1's token
        'bio': "Attempted update by another professional."
    })
    assert response.status_code == 403
    assert response.json['error'] == 'Não autorizado a atualizar este perfil'


@pytest.fixture(scope="module", autouse=True)
def cleanup_professional_profile_test_data(app_context, test_data_professional_profile):
    yield # allow tests to run
    with app_context:
        emails_to_delete = [
            'admin_prof_profile@test.com',
            'prof1_profile@test.com',
            'prof2_profile@test.com'
        ]
        users = User.query.filter(User.email.in_(emails_to_delete)).all()
        for user in users:
            Professional.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
        db.session.commit()
