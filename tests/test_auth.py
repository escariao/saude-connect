import pytest
from flask import current_app
from src.models.user import User, db
from src.models.professional import Professional, Activity, ProfessionalActivity
from src.models.category import Category
import os # For file path checks

# --- Test Data Setup for Auth Tests ---
@pytest.fixture(scope='module')
def test_data_auth(app_context):
    with app_context:
        # Category for activities
        category_auth = Category.query.filter_by(name='Auth Test Category').first()
        if not category_auth:
            category_auth = Category(name='Auth Test Category')
            db.session.add(category_auth)
            db.session.flush()

        # Global Activities for selection during registration
        activity_auth1 = Activity.query.filter_by(name='Auth Test Activity 1').first()
        if not activity_auth1:
            activity_auth1 = Activity(name='Auth Test Activity 1', description='Global desc 1', category_id=category_auth.id)
            db.session.add(activity_auth1)

        activity_auth2 = Activity.query.filter_by(name='Auth Test Activity 2').first()
        if not activity_auth2:
            activity_auth2 = Activity(name='Auth Test Activity 2', description='Global desc 2', category_id=category_auth.id)
            db.session.add(activity_auth2)
        
        db.session.commit()
        return {
            "activity1_id": activity_auth1.id,
            "activity2_id": activity_auth2.id,
            "upload_folder": current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static', 'uploads'))
        }

# --- Existing Patient Registration and Login Tests (Assumed to be kept and potentially refactored if needed) ---

def test_register_patient_success(client):
    response = client.post('/api/auth/register/patient', json={
        'email': 'patient_auth@example.com',
        'password': current_app.config['TEST_USER_PASSWORD'],
        'name': 'Patient Auth User',
        'document': 'AUTH123456'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'user_id' in data

def test_register_patient_missing_fields(client):
    response = client.post('/api/auth/register/patient', json={
        'email': 'patient_auth_missing@example.com'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_register_patient_duplicate_email(client):
    client.post('/api/auth/register/patient', json={
        'email': 'patient_auth_dup@example.com',
        'password': current_app.config['TEST_USER_PASSWORD'],
        'name': 'Patient Auth Dup',
        'document': 'AUTH_DUP123'
    })
    response = client.post('/api/auth/register/patient', json={
        'email': 'patient_auth_dup@example.com',
        'password': current_app.config['TEST_USER_PASSWORD'],
        'name': 'Patient Auth Dup2',
        'document': 'AUTH_DUP456'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Email já cadastrado' in data['error']


def test_login_success_patient(client):
    email = 'login_auth_patient@example.com'
    password = current_app.config['TEST_USER_PASSWORD']
    client.post('/api/auth/register/patient', json={
        'email': email,
        'password': password,
        'name': 'Login Auth Patient',
        'document': 'LOGIN_AUTH_P'
    })
    response = client.post('/api/auth/login', json={'email': email, 'password': password})
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert data['user']['email'] == email
    assert data['user']['user_type'] == 'patient'

def test_login_incorrect_password(client):
    email = 'login_fail_auth@example.com'
    password = current_app.config['TEST_USER_PASSWORD']
    client.post('/api/auth/register/patient', json={
        'email': email,
        'password': password,
        'name': 'Login Fail Auth',
        'document': 'LOGIN_FAIL_AUTH'
    })
    response = client.post('/api/auth/login', json={'email': email, 'password': 'wrongpassword'})
    assert response.status_code == 401
    data = response.get_json()
    assert 'message' in data
    assert 'Email ou senha incorretos' in data['message']

# --- Professional Registration Tests (Sub-task 6.3) ---

@pytest.fixture
def dummy_diploma_file(tmp_path):
    d = tmp_path / "diplomas"
    d.mkdir()
    p = d / "dummy_diploma.pdf"
    p.write_text("This is a dummy PDF content.")
    return p

def test_register_professional_success_with_activities(client, test_data_auth, dummy_diploma_file):
    upload_folder = test_data_auth['upload_folder']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    data = {
        'email': 'prof_auth1@example.com',
        'password': current_app.config['TEST_USER_PASSWORD'],
        'name': 'Professional Auth One',
        'document': 'PROF_AUTH001',
        'bio': 'Bio for prof auth one.',
        'activity_ids[]': [str(test_data_auth['activity1_id']), str(test_data_auth['activity2_id'])],
        'activity_descriptions[]': ['Custom desc for activity 1', 'Custom desc for activity 2'],
        'activity_prices[]': ['150.00', '200.50']
    }
    files = {'diploma': (dummy_diploma_file.name, dummy_diploma_file.open('rb'), 'application/pdf')}
    
    response = client.post('/api/auth/register/professional', data=data, files=files, content_type='multipart/form-data')
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert 'user_id' in json_data
    
    user = User.query.filter_by(email='prof_auth1@example.com').first()
    assert user is not None
    professional = Professional.query.filter_by(user_id=user.id).first()
    assert professional is not None
    assert professional.bio == 'Bio for prof auth one.'
    assert os.path.exists(os.path.join(upload_folder, professional.diploma_file)) # Check if file was "saved"

    prof_activities = ProfessionalActivity.query.filter_by(professional_id=professional.id).all()
    assert len(prof_activities) == 2
    
    act1_data = next((pa for pa in prof_activities if pa.activity_id == test_data_auth['activity1_id']), None)
    assert act1_data is not None
    assert act1_data.description == 'Custom desc for activity 1'
    assert act1_data.price == 150.00
    
    act2_data = next((pa for pa in prof_activities if pa.activity_id == test_data_auth['activity2_id']), None)
    assert act2_data is not None
    assert act2_data.description == 'Custom desc for activity 2'
    assert act2_data.price == 200.50

def test_register_professional_success_no_activities(client, test_data_auth, dummy_diploma_file):
    upload_folder = test_data_auth['upload_folder']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    data = {
        'email': 'prof_auth2@example.com',
        'password': current_app.config['TEST_USER_PASSWORD'],
        'name': 'Professional Auth Two (No Activities)',
        'document': 'PROF_AUTH002',
        'bio': 'Bio for prof auth two.'
        # No activity_ids[], descriptions, or prices
    }
    files = {'diploma': (dummy_diploma_file.name, dummy_diploma_file.open('rb'), 'application/pdf')}
    
    response = client.post('/api/auth/register/professional', data=data, files=files, content_type='multipart/form-data')
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert 'user_id' in json_data
    
    user = User.query.filter_by(email='prof_auth2@example.com').first()
    assert user is not None
    professional = Professional.query.filter_by(user_id=user.id).first()
    assert professional is not None
    
    prof_activities = ProfessionalActivity.query.filter_by(professional_id=professional.id).all()
    assert len(prof_activities) == 0 # Should have no professional activities

def test_register_professional_invalid_activity_id(client, test_data_auth, dummy_diploma_file):
    upload_folder = test_data_auth['upload_folder']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    data = {
        'email': 'prof_auth3@example.com',
        'password': current_app.config['TEST_USER_PASSWORD'],
        'name': 'Professional Auth Three (Invalid Activity)',
        'document': 'PROF_AUTH003',
        'activity_ids[]': [str(test_data_auth['activity1_id']), '99999'], # 99999 is invalid
        'activity_descriptions[]': ['Desc for valid activity', 'Desc for invalid'],
        'activity_prices[]': ['100.00', '50.00']
    }
    files = {'diploma': (dummy_diploma_file.name, dummy_diploma_file.open('rb'), 'application/pdf')}
    
    response = client.post('/api/auth/register/professional', data=data, files=files, content_type='multipart/form-data')
    
    assert response.status_code == 201 # Registration itself should succeed
    json_data = response.get_json()
    user_id = json_data['user_id']
    
    professional = Professional.query.join(User).filter(User.id == user_id).first()
    assert professional is not None
    
    # Only the valid activity should have been created
    prof_activities = ProfessionalActivity.query.filter_by(professional_id=professional.id).all()
    assert len(prof_activities) == 1 
    assert prof_activities[0].activity_id == test_data_auth['activity1_id']
    assert prof_activities[0].description == 'Desc for valid activity'
    assert prof_activities[0].price == 100.00

def test_register_professional_missing_diploma(client, test_data_auth):
    data = {
        'email': 'prof_auth4@example.com',
        'password': current_app.config['TEST_USER_PASSWORD'],
        'name': 'Professional Auth Four (No Diploma)',
        'document': 'PROF_AUTH004'
    }
    # No files dictionary passed
    response = client.post('/api/auth/register/professional', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'Diploma é obrigatório' in json_data['error']


@pytest.fixture(scope="module", autouse=True)
def cleanup_auth_test_data(app_context, test_data_auth):
    yield # allow tests to run
    with app_context:
        # Clean up users created in these tests
        emails_to_delete = [
            'patient_auth@example.com', 
            'patient_auth_missing@example.com', # This one was not created
            'patient_auth_dup@example.com',
            'login_auth_patient@example.com',
            'login_fail_auth@example.com',
            'prof_auth1@example.com',
            'prof_auth2@example.com',
            'prof_auth3@example.com',
            'prof_auth4@example.com' # This one was not created
        ]
        users = User.query.filter(User.email.in_(emails_to_delete)).all()
        for user in users:
            # Delete associated Professional and ProfessionalActivity entries
            prof = Professional.query.filter_by(user_id=user.id).first()
            if prof:
                ProfessionalActivity.query.filter_by(professional_id=prof.id).delete()
                db.session.delete(prof)
            db.session.delete(user)

        # Clean up activities and category
        Activity.query.filter_by(id=test_data_auth['activity1_id']).delete()
        Activity.query.filter_by(id=test_data_auth['activity2_id']).delete()
        Category.query.filter(Category.name == 'Auth Test Category').delete()
        
        db.session.commit()

        # Clean up dummy diploma files if any were "saved" (though they are in tmp_path usually)
        # For the UPLOAD_FOLDER, manual cleanup might be needed if files are actually written there by tests.
        # This part is tricky without knowing the exact file saving mock strategy.
        # If files are saved to UPLOAD_FOLDER, they should be cleaned.
        # Example:
        # for root, dirs, files_in_dir in os.walk(test_data_auth['upload_folder']):
        #    for f_name in files_in_dir:
        #        if "dummy_diploma" in f_name or "PROF_AUTH" in f_name: # Be careful with patterns
        #            try:
        #                os.remove(os.path.join(root, f_name))
        #            except OSError:
        #                pass # File might have been removed by another test or not created
    
    # The dummy_diploma_file fixture handles its own cleanup due to tmp_path.
    # We need to handle cleanup of files in the actual UPLOAD_FOLDER if the app writes there.
    # The test `test_register_professional_success_with_activities` checks `os.path.exists`
    # which implies it expects the app to write to `UPLOAD_FOLDER`.
    # Let's add a basic cleanup for that, assuming `professional.diploma_file` stores only the filename.
    with app_context:
        professionals_for_cleanup = Professional.query.join(User).filter(User.email.like('prof_auth%@example.com')).all()
        upload_folder = test_data_auth['upload_folder']
        for prof in professionals_for_cleanup:
            if prof.diploma_file:
                file_path_to_remove = os.path.join(upload_folder, prof.diploma_file)
                if os.path.exists(file_path_to_remove):
                    try:
                        os.remove(file_path_to_remove)
                    except Exception as e:
                        print(f"Warning: Could not remove test diploma file {file_path_to_remove}: {e}")
        db.session.commit() # Commit any session changes from querying above
