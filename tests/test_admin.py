import pytest
from flask import current_app
from datetime import datetime
from src.models.user import User, db
from src.models.professional import Professional, Activity
from src.models.category import Category
from src.models.professional_activity import ProfessionalActivity

@pytest.fixture(scope='module')
def test_data_admin(app_context):
    """Creates initial data for admin tests."""
    with app_context:
        admin_user = User.query.filter_by(email='admin_adm@test.com').first()
        if not admin_user:
            admin_user = User(email='admin_adm@test.com', password=current_app.config['TEST_USER_PASSWORD'], name='Admin User Admin', user_type='admin', approval_status='approved')
            db.session.add(admin_user)

        pending_prof_user = User.query.filter_by(email='pending_prof_adm@test.com').first()
        if not pending_prof_user:
            pending_prof_user = User(email='pending_prof_adm@test.com', password=current_app.config['TEST_USER_PASSWORD'], name='Pending Prof Admin', user_type='professional', approval_status='pending')
            db.session.add(pending_prof_user)
        
        approved_prof_user = User.query.filter_by(email='approved_prof_adm@test.com').first()
        if not approved_prof_user:
            approved_prof_user = User(email='approved_prof_adm@test.com', password=current_app.config['TEST_USER_PASSWORD'], name='Approved Prof Admin', user_type='professional', approval_status='approved')
            db.session.add(approved_prof_user)

        patient_user_adm = User.query.filter_by(email='patient_adm@test.com').first()
        if not patient_user_adm:
            patient_user_adm = User(email='patient_adm@test.com', password=current_app.config['TEST_USER_PASSWORD'], name='Patient User Admin', user_type='patient', approval_status='approved')
            db.session.add(patient_user_adm)

        db.session.flush() # Ensure IDs are available

        pending_professional = Professional.query.filter_by(user_id=pending_prof_user.id).first()
        if not pending_professional:
            pending_professional = Professional(user_id=pending_prof_user.id, document_number='ADM001', diploma_file='dp_adm001.pdf', bio='Pending approval.')
            db.session.add(pending_professional)

        approved_professional = Professional.query.filter_by(user_id=approved_prof_user.id).first()
        if not approved_professional:
            approved_professional = Professional(user_id=approved_prof_user.id, document_number='ADM002', diploma_file='dp_adm002.pdf', bio='Already approved.', approval_status='approved')
            db.session.add(approved_professional)
        
        category1 = Category.query.filter_by(name='Test Category Admin 1').first()
        if not category1:
            category1 = Category(name='Test Category Admin 1')
            db.session.add(category1)
            db.session.flush() # Ensure category1.id is available
        
        activity1 = Activity.query.filter_by(name='Test Activity Admin 1').first()
        if not activity1:
            activity1 = Activity(name='Test Activity Admin 1', description='Desc for activity 1', category_id=category1.id)
            db.session.add(activity1)
            
        activity2 = Activity.query.filter_by(name='Test Activity Admin 2 Unused').first()
        if not activity2:
            activity2 = Activity(name='Test Activity Admin 2 Unused', description='Desc for activity 2')
            db.session.add(activity2)

        db.session.commit()
        return {
            "admin_user_id": admin_user.id,
            "patient_user_id": patient_user_adm.id,
            "pending_prof_user_id": pending_prof_user.id, # Added for direct access
            "pending_prof_id": pending_professional.id,
            "approved_prof_id": approved_professional.id,
            "activity1_id": activity1.id,
            "activity2_id": activity2.id,
            "category1_id": category1.id
        }

@pytest.fixture(scope='module')
def auth_headers_admin(client, test_data_admin): # Depends on test_data_admin
    admin_login_res = client.post('/api/auth/login', json={'email': 'admin_adm@test.com', 'password': current_app.config['TEST_USER_PASSWORD']})
    admin_token = admin_login_res.json['token']
    
    patient_login_res = client.post('/api/auth/login', json={'email': 'patient_adm@test.com', 'password': current_app.config['TEST_USER_PASSWORD']})
    patient_token = patient_login_res.json['token']
    
    return {
        'admin': {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'},
        'patient': {'Authorization': f'Bearer {patient_token}', 'Content-Type': 'application/json'}
    }

# --- Professional Management Tests ---
def test_admin_lists_pending_professionals(client, auth_headers_admin, test_data_admin):
    response = client.get('/admin/professionals/pending', headers=auth_headers_admin['admin'])
    assert response.status_code == 200
    assert isinstance(response.json, list)
    found = any(prof['id'] == test_data_admin['pending_prof_id'] for prof in response.json)
    assert found 

def test_admin_approves_pending_professional(client, auth_headers_admin, test_data_admin):
    prof_id = test_data_admin['pending_prof_id']
    user_id = test_data_admin['pending_prof_user_id']

    # Ensure it's pending before test
    prof_before = Professional.query.get(prof_id)
    assert prof_before.approval_status == 'pending'
    user_before = User.query.get(user_id)
    assert user_before.approval_status == 'pending'
    
    response = client.post(f'/admin/professionals/{prof_id}/approve', headers=auth_headers_admin['admin'])
    assert response.status_code == 200
    assert response.json['message'] == 'Profissional aprovado com sucesso'
    
    prof_after = Professional.query.get(prof_id)
    assert prof_after.approval_status == 'approved'
    user_after = User.query.get(user_id)
    assert user_after.approval_status == 'approved'

def test_admin_rejects_pending_professional(client, auth_headers_admin, app_context):
    # Create a fresh pending professional for this test to avoid state issues
    with app_context:
        temp_user = User(email='temp_reject_adm@test.com', password=current_app.config['TEST_USER_PASSWORD'], name='Temp Reject Admin', user_type='professional', approval_status='pending')
        db.session.add(temp_user)
        db.session.flush()
        temp_prof = Professional(user_id=temp_user.id, document_number='TRJADM01', diploma_file='trjadm.pdf', approval_status='pending')
        db.session.add(temp_prof)
        db.session.commit()
        temp_prof_id = temp_prof.id
        temp_user_id = temp_user.id

    response = client.post(f'/admin/professionals/{temp_prof_id}/reject', headers=auth_headers_admin['admin'], json={'reason': 'Test rejection admin'})
    assert response.status_code == 200
    assert response.json['message'] == 'Profissional rejeitado com sucesso'
    
    prof = Professional.query.get(temp_prof_id)
    assert prof.approval_status == 'rejected'
    assert prof.rejection_reason == 'Test rejection admin'
    user = User.query.get(temp_user_id)
    assert user.approval_status == 'rejected'

def test_admin_approves_already_approved_professional(client, auth_headers_admin, test_data_admin):
    prof_id = test_data_admin['approved_prof_id']
    response = client.post(f'/admin/professionals/{prof_id}/approve', headers=auth_headers_admin['admin'])
    assert response.status_code == 400 
    assert "already approved" in response.json['message'].lower() # Make check case-insensitive

def test_non_admin_access_professional_management(client, auth_headers_admin, test_data_admin):
    prof_id = test_data_admin['pending_prof_id']
    response_get = client.get('/admin/professionals/pending', headers=auth_headers_admin['patient'])
    assert response_get.status_code == 403
    
    response_post = client.post(f'/admin/professionals/{prof_id}/approve', headers=auth_headers_admin['patient'])
    assert response_post.status_code == 403

# --- Activity Management Tests ---
def test_admin_lists_activities(client, auth_headers_admin, test_data_admin):
    response = client.get('/admin/activities', headers=auth_headers_admin['admin'])
    assert response.status_code == 200
    assert isinstance(response.json, list)
    found = any(act['id'] == test_data_admin['activity1_id'] for act in response.json)
    assert found

def test_admin_adds_activity_with_category(client, auth_headers_admin, test_data_admin):
    response = client.post('/admin/activities', headers=auth_headers_admin['admin'], json={
        'name': 'New Activity With Cat Admin',
        'description': 'A new one for admin.',
        'category_id': test_data_admin['category1_id']
    })
    assert response.status_code == 201
    assert response.json['name'] == 'New Activity With Cat Admin'
    assert response.json['category']['id'] == test_data_admin['category1_id']

def test_admin_adds_activity_without_category(client, auth_headers_admin):
    response = client.post('/admin/activities', headers=auth_headers_admin['admin'], json={
        'name': 'New Activity No Cat Admin',
        'description': 'Another new one for admin.'
    })
    assert response.status_code == 201
    assert response.json['name'] == 'New Activity No Cat Admin'
    assert response.json['category'] is None

def test_admin_adds_activity_duplicate_name(client, auth_headers_admin, test_data_admin):
    response = client.post('/admin/activities', headers=auth_headers_admin['admin'], json={
        'name': 'Test Activity Admin 1', 
        'description': 'Trying to duplicate for admin.'
    })
    assert response.status_code == 409

def test_admin_updates_activity(client, auth_headers_admin, test_data_admin):
    activity_id_to_update = test_data_admin['activity1_id']
    response = client.put(f'/admin/activities/{activity_id_to_update}', headers=auth_headers_admin['admin'], json={
        'name': 'Updated Activity Name Admin',
        'description': 'Updated description for admin.'
    })
    assert response.status_code == 200
    assert response.json['name'] == 'Updated Activity Name Admin'
    assert response.json['description'] == 'Updated description for admin.'

def test_admin_deletes_unused_activity(client, auth_headers_admin, test_data_admin):
    activity_id_to_delete = test_data_admin['activity2_id'] 
    response = client.delete(f'/admin/activities/{activity_id_to_delete}', headers=auth_headers_admin['admin'])
    assert response.status_code == 200
    assert response.json['message'] == 'Activity deleted successfully'

def test_admin_deletes_used_activity_fail(client, auth_headers_admin, test_data_admin, app_context):
    with app_context:
        # Ensure activity1 is used by the approved_professional
        prof_activity = ProfessionalActivity.query.filter_by(
            professional_id=test_data_admin['approved_prof_id'],
            activity_id=test_data_admin['activity1_id']
        ).first()
        if not prof_activity:
            prof_activity = ProfessionalActivity(
                professional_id=test_data_admin['approved_prof_id'],
                activity_id=test_data_admin['activity1_id'],
                description="Service provided by admin test setup",
                price=100
            )
            db.session.add(prof_activity)
            db.session.commit()

    activity_id_to_delete = test_data_admin['activity1_id']
    response = client.delete(f'/admin/activities/{activity_id_to_delete}', headers=auth_headers_admin['admin'])
    assert response.status_code == 400 
    assert "Activity is in use" in response.json['message']

def test_non_admin_access_activity_management(client, auth_headers_admin, test_data_admin):
    response_get = client.get('/admin/activities', headers=auth_headers_admin['patient'])
    assert response_get.status_code == 403
    
    response_post = client.post('/admin/activities', headers=auth_headers_admin['patient'], json={'name': 'Attempt Admin'})
    assert response_post.status_code == 403

# --- Category Management Test (Listing only, as per current routes) ---
def test_admin_lists_categories_from_search_route(client, auth_headers_admin, test_data_admin):
    # The get_categories route is under /api/search and made public in Task 4.
    # Admins should also be able to access it.
    response = client.get('/api/search/categories', headers=auth_headers_admin['admin']) 
    assert response.status_code == 200
    assert isinstance(response.json, list)
    found = any(cat['id'] == test_data_admin['category1_id'] for cat in response.json)
    assert found

# Note: Full CRUD for Categories by Admin would require dedicated /admin/categories routes.
# These tests assume only the existing routes are being tested.

@pytest.fixture(scope="module", autouse=True)
def cleanup_admin_test_data(app_context, test_data_admin):
    yield # allow tests to run

    with app_context:
        # Delete ProfessionalActivities linked for cleanup
        ProfessionalActivity.query.filter_by(professional_id=test_data_admin['approved_prof_id'], activity_id=test_data_admin['activity1_id']).delete()
        
        # Delete specific activities created by tests if their names are known and unique
        Activity.query.filter(Activity.name.in_([
            'New Activity With Cat Admin', 
            'New Activity No Cat Admin',
            'Updated Activity Name Admin' # if update changed name from original fixture
        ])).delete()
        
        # Attempt to delete fixture activities (they might have been deleted by tests)
        for act_id_key in ['activity1_id', 'activity2_id']:
            try:
                act = Activity.query.get(test_data_admin[act_id_key])
                if act: db.session.delete(act)
            except: pass # Ignore if already deleted

        # Attempt to delete fixture category
        try:
            cat = Category.query.get(test_data_admin['category1_id'])
            if cat: db.session.delete(cat)
        except: pass

        # Delete users
        emails_to_delete = [
            'admin_adm@test.com', 
            'pending_prof_adm@test.com', 
            'approved_prof_adm@test.com', 
            'patient_adm@test.com', 
            'temp_reject_adm@test.com'
        ]
        users = User.query.filter(User.email.in_(emails_to_delete)).all()
        for user in users:
            Professional.query.filter_by(user_id=user.id).delete() # Delete linked professionals
            db.session.delete(user)
        
        db.session.commit()
