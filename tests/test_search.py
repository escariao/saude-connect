import pytest
from flask import current_app
from src.models.user import User, db
from src.models.professional import Professional, Activity
from src.models.category import Category
from src.models.professional_activity import ProfessionalActivity
from datetime import datetime

@pytest.fixture(scope='module')
def test_data_search(app_context):
    with app_context:
        # Users
        search_user = User.query.filter_by(email='search_user_main@test.com').first()
        if not search_user: # For auth header if needed by some tests, though many search routes are public
            search_user = User(email='search_user_main@test.com', password=current_app.config['TEST_USER_PASSWORD'], name='Search User Main', user_type='patient', approval_status='approved')
            db.session.add(search_user)

        prof_user_search1 = User.query.filter_by(email='prof_search1@test.com').first()
        if not prof_user_search1:
            prof_user_search1 = User(email='prof_search1@test.com', password=current_app.config['TEST_USER_PASSWORD'], name='Search Prof One', user_type='professional', approval_status='approved')
            db.session.add(prof_user_search1)

        prof_user_search2 = User.query.filter_by(email='prof_search2@test.com').first()
        if not prof_user_search2:
            prof_user_search2 = User(email='prof_search2@test.com', password=current_app.config['TEST_USER_PASSWORD'], name='Search Prof Two', user_type='professional', approval_status='approved')
            db.session.add(prof_user_search2)
        
        db.session.flush()

        # Categories
        category_search1 = Category.query.filter_by(name='Cardiology Search').first()
        if not category_search1:
            category_search1 = Category(name='Cardiology Search')
            db.session.add(category_search1)

        category_search2 = Category.query.filter_by(name='Neurology Search').first()
        if not category_search2:
            category_search2 = Category(name='Neurology Search')
            db.session.add(category_search2)
        db.session.flush()

        # Global Activities
        activity_search_cardio = Activity.query.filter_by(name='ECG Test').first()
        if not activity_search_cardio:
            activity_search_cardio = Activity(name='ECG Test', description='Electrocardiogram', category_id=category_search1.id)
            db.session.add(activity_search_cardio)

        activity_search_neuro = Activity.query.filter_by(name='EEG Test').first()
        if not activity_search_neuro:
            activity_search_neuro = Activity(name='EEG Test', description='Electroencephalogram', category_id=category_search2.id)
            db.session.add(activity_search_neuro)
        
        activity_search_general = Activity.query.filter_by(name='General Consultation Search').first()
        if not activity_search_general:
            activity_search_general = Activity(name='General Consultation Search', description='General checkup') # No category
            db.session.add(activity_search_general)
        db.session.flush()

        # Professionals
        prof1 = Professional.query.filter_by(user_id=prof_user_search1.id).first()
        if not prof1:
            prof1 = Professional(user_id=prof_user_search1.id, document_number='SRPS001', diploma_file='srps1.pdf', bio='Cardiologist specialist.', approval_status='approved', approval_date=datetime.utcnow())
            db.session.add(prof1)

        prof2 = Professional.query.filter_by(user_id=prof_user_search2.id).first()
        if not prof2:
            prof2 = Professional(user_id=prof_user_search2.id, document_number='SRPS002', diploma_file='srps2.pdf', bio='Neurologist and generalist.', approval_status='approved', approval_date=datetime.utcnow())
            db.session.add(prof2)
        db.session.flush()

        # Professional Activities (linking)
        # Prof1 offers ECG
        pa1_1 = ProfessionalActivity.query.filter_by(professional_id=prof1.id, activity_id=activity_search_cardio.id).first()
        if not pa1_1:
            pa1_1 = ProfessionalActivity(professional_id=prof1.id, activity_id=activity_search_cardio.id, description='ECG for adults', price=150.00, availability='Mon-Fri')
            db.session.add(pa1_1)
        
        # Prof2 offers EEG and General Consultation
        pa2_1 = ProfessionalActivity.query.filter_by(professional_id=prof2.id, activity_id=activity_search_neuro.id).first()
        if not pa2_1:
            pa2_1 = ProfessionalActivity(professional_id=prof2.id, activity_id=activity_search_neuro.id, description='EEG for all ages', price=250.00, availability='Tue, Thu')
            db.session.add(pa2_1)
        
        pa2_2 = ProfessionalActivity.query.filter_by(professional_id=prof2.id, activity_id=activity_search_general.id).first()
        if not pa2_2:
            pa2_2 = ProfessionalActivity(professional_id=prof2.id, activity_id=activity_search_general.id, description='Quick checkup', price=100.00, availability='Mon-Wed')
            db.session.add(pa2_2)

        db.session.commit()
        return {
            "prof1_id": prof1.id, "prof1_user_id": prof_user_search1.id, "prof1_name": prof_user_search1.name,
            "prof2_id": prof2.id, "prof2_user_id": prof_user_search2.id, "prof2_name": prof_user_search2.name,
            "activity_cardio_id": activity_search_cardio.id, "activity_cardio_name": activity_search_cardio.name,
            "activity_neuro_id": activity_search_neuro.id, "activity_neuro_name": activity_search_neuro.name,
            "activity_general_id": activity_search_general.id,
            "category_cardio_name": category_search1.name,
            "category_neuro_name": category_search2.name,
            "search_user_email": search_user.email
        }

@pytest.fixture(scope='module')
def auth_headers_search(client, test_data_search):
    # This token is for routes that might still be protected, though many search routes are public.
    login_res = client.post('/api/auth/login', json={'email': test_data_search['search_user_email'], 'password': current_app.config['TEST_USER_PASSWORD']})
    token = login_res.json['token']
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


# --- Test Search Professionals ---
def test_search_professionals_by_activity_id(client, auth_headers_search, test_data_search):
    response = client.get(f"/api/search/professionals?activity_id={test_data_search['activity_cardio_id']}", headers=auth_headers_search)
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(prof['id'] == test_data_search['prof1_id'] for prof in data)
    assert not any(prof['id'] == test_data_search['prof2_id'] for prof in data) # Prof2 doesn't offer cardio_id directly

def test_search_professionals_by_category_name(client, auth_headers_search, test_data_search):
    response = client.get(f"/api/search/professionals?category={test_data_search['category_neuro_name']}", headers=auth_headers_search)
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) >= 1
    # Prof2 offers EEG which is in Neurology Search category
    assert any(prof['id'] == test_data_search['prof2_id'] for prof in data)
    # Prof1 only offers Cardiology Search activity
    assert not any(prof['id'] == test_data_search['prof1_id'] for prof in data)

def test_search_professionals_by_name(client, auth_headers_search, test_data_search):
    response = client.get(f"/api/search/professionals?name=Search Prof One", headers=auth_headers_search) # Matches prof1_name
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['id'] == test_data_search['prof1_id']
    assert data[0]['name'] == test_data_search['prof1_name']

def test_search_professionals_by_activity_and_name(client, auth_headers_search, test_data_search):
    response = client.get(f"/api/search/professionals?activity_id={test_data_search['activity_general_id']}&name=Search Prof Two", headers=auth_headers_search)
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]['id'] == test_data_search['prof2_id']

def test_search_professionals_no_results(client, auth_headers_search, test_data_search):
    response = client.get(f"/api/search/professionals?name=NonExistentNameXYZ", headers=auth_headers_search)
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) == 0

def test_search_professional_response_structure(client, auth_headers_search, test_data_search):
    response = client.get(f"/api/search/professionals?activity_id={test_data_search['activity_cardio_id']}", headers=auth_headers_search)
    assert response.status_code == 200
    data = response.json
    assert len(data) > 0
    prof_data = data[0]
    assert 'id' in prof_data
    assert 'name' in prof_data
    assert 'bio' in prof_data
    assert 'activities' in prof_data
    assert isinstance(prof_data['activities'], list)
    if prof_data['activities']:
        activity_detail = prof_data['activities'][0]
        assert 'professional_activity_id' in activity_detail
        assert 'activity_id' in activity_detail
        assert 'activity_name' in activity_detail
        assert 'activity_description' in activity_detail # Global activity desc
        assert 'professional_description' in activity_detail # Professional's desc for this activity
        assert 'price' in activity_detail
        assert 'availability' in activity_detail
        assert 'category' in activity_detail # Category name or null
        assert activity_detail['activity_name'] == test_data_search['activity_cardio_name']


# --- Test List Global Activities (Public) ---
def test_list_global_activities_public(client, test_data_search): # No auth_headers
    response = client.get('/api/search/activities')
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) >= 3 # At least the 3 created in fixture
    
    # Check for one of the activities
    found_cardio = any(act['name'] == test_data_search['activity_cardio_name'] and act['category'] == test_data_search['category_cardio_name'] for act in data)
    assert found_cardio
    found_general = any(act['name'] == 'General Consultation Search' and act['category'] is None for act in data)
    assert found_general

# --- Test List Categories (Public) ---
def test_list_categories_public(client, test_data_search): # No auth_headers
    response = client.get('/api/search/categories')
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) >= 2 # At least the 2 created in fixture
    
    found_cardio_cat = any(cat['name'] == test_data_search['category_cardio_name'] for cat in data)
    assert found_cardio_cat
    found_neuro_cat = any(cat['name'] == test_data_search['category_neuro_name'] for cat in data)
    assert found_neuro_cat

# --- Test Get Professional Details (Public or Protected based on final decision) ---
# Assuming this route is protected as per original test file structure
def test_get_professional_details_search(client, auth_headers_search, test_data_search):
    prof_id_to_get = test_data_search['prof1_id']
    response = client.get(f'/api/search/professional/{prof_id_to_get}', headers=auth_headers_search)
    assert response.status_code == 200
    data = response.json
    assert data['id'] == prof_id_to_get
    assert data['name'] == test_data_search['prof1_name']
    assert 'activities' in data
    assert len(data['activities']) > 0
    # Further checks on activity structure similar to test_search_professional_response_structure can be added

def test_get_professional_details_not_found(client, auth_headers_search):
    response = client.get('/api/search/professional/99999', headers=auth_headers_search) # Non-existent ID
    assert response.status_code == 404
    assert 'error' in response.json
    assert 'Profissional não encontrado' in response.json['error']


@pytest.fixture(scope="module", autouse=True)
def cleanup_search_test_data(app_context, test_data_search):
    yield # allow tests to run
    with app_context:
        # Delete ProfessionalActivities
        # Need to be careful here, if other tests created PAs for these professionals/activities
        # This cleanup is primarily for PAs created *within* test_data_search setup.
        # A more robust way would be to store IDs of created PAs in test_data_search and delete those.
        # For now, let's assume this is okay, or rely on cascading deletes if configured.
        ProfessionalActivity.query.filter(ProfessionalActivity.activity_id.in_([
            test_data_search['activity_cardio_id'], 
            test_data_search['activity_neuro_id'],
            test_data_search['activity_general_id']
        ])).delete()

        # Delete Professionals
        Professional.query.filter(Professional.id.in_([test_data_search['prof1_id'], test_data_search['prof2_id']])).delete()
        
        # Delete Users
        User.query.filter(User.email.in_([
            test_data_search['search_user_email'], 
            'prof_search1@test.com', 
            'prof_search2@test.com'
        ])).delete()
        
        # Delete Activities
        Activity.query.filter(Activity.id.in_([
            test_data_search['activity_cardio_id'], 
            test_data_search['activity_neuro_id'],
            test_data_search['activity_general_id']
        ])).delete()
        
        # Delete Categories
        Category.query.filter(Category.name.in_([
            test_data_search['category_cardio_name'], 
            test_data_search['category_neuro_name']
        ])).delete()
        
        db.session.commit()
