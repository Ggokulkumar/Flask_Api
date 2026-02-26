import pytest
import json
import os
import config
import db
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    config.DATABASE = 'test_users.db'

    if os.path.exists('test_users.db'):
        os.remove('test_users.db')

    db.init_db()

    with app.test_client() as client:
        yield client

    config.DATABASE = 'users.db'
    if os.path.exists('test_users.db'):
        os.remove('test_users.db')


def test_get_users(client):
    response = client.get('/api/users')
    data = response.get_json()

    assert response.status_code == 200
    assert 'users' in data
    assert 'total' in data
    assert 'page' in data
    assert len(data['users']) <= data['limit']


def test_get_users_pagination(client):
    response = client.get('/api/users?page=1&limit=3')
    data = response.get_json()

    assert response.status_code == 200
    assert len(data['users']) == 3
    assert data['page'] == 1
    assert data['limit'] == 3


def test_get_users_search(client):
    response = client.get('/api/users?search=James')
    data = response.get_json()

    assert response.status_code == 200
    assert len(data['users']) >= 1


def test_get_users_sort(client):
    response = client.get('/api/users?sort=-age&limit=10')
    data = response.get_json()

    assert response.status_code == 200
    ages = [u['age'] for u in data['users']]
    assert ages == sorted(ages, reverse=True)


def test_create_user(client):
    new_user = {
        'first_name': 'Gokul',
        'last_name': 'Kumar',
        'company_name': 'HPE',
        'age': 22,
        'city': 'Bangalore',
        'state': 'KA',
        'zip': '560048',
        'email': 'gokul@test.com',
        'web': 'http://test.com'
    }
    response = client.post('/api/users',
                           data=json.dumps(new_user),
                           content_type='application/json')
    data = response.get_json()

    assert response.status_code == 201
    assert data['message'] == 'User created'
    assert 'id' in data


def test_create_user_missing_fields(client):
    response = client.post('/api/users',
                           data=json.dumps({'age': 25}),
                           content_type='application/json')

    assert response.status_code == 400


def test_get_user_by_id(client):
    response = client.get('/api/users/1')
    data = response.get_json()

    assert response.status_code == 200
    assert data['id'] == 1
    assert 'first_name' in data


def test_get_user_not_found(client):
    response = client.get('/api/users/9999')

    assert response.status_code == 404


def test_update_user(client):
    updated = {
        'first_name': 'Updated',
        'last_name': 'Name',
        'company_name': 'New Corp',
        'age': 40,
        'city': 'NewCity',
        'state': 'NY',
        'zip': '10001',
        'email': 'updated@test.com',
        'web': 'http://updated.com'
    }
    response = client.put('/api/users/1',
                          data=json.dumps(updated),
                          content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['message'] == 'User updated'


def test_delete_user(client):
    response = client.delete('/api/users/1')
    assert response.status_code == 200

    response = client.get('/api/users/1')
    assert response.status_code == 404


def test_patch_user(client):
    response = client.patch('/api/users/2',
                            data=json.dumps({'age': 99}),
                            content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['message'] == 'User partially updated'

    response = client.get('/api/users/2')
    assert response.get_json()['age'] == 99


def test_summary(client):
    response = client.get('/api/users/summary')
    data = response.get_json()

    assert response.status_code == 200
    assert 'total_users' in data
    assert 'average_age' in data
    assert 'count_by_city' in data
