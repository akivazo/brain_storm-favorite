import pytest

from flask.testing import FlaskClient
from mongomock import MongoClient
from ..favorite_api import server, set_mongo_client

@pytest.fixture
def client():
    # Create a mock MongoDB client
    mock_mongo_client = MongoClient()
    set_mongo_client(mock_mongo_client)
    server.config['TESTING'] = True
    # Set up Flask test client
    client = server.test_client()
    yield client
    mock_mongo_client.close()


def test_root_endpoint(client: FlaskClient):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Favorite Api"

def test_add_favorite(client: FlaskClient):
    response = client.post('/favorite/JohnDoe/idea_id1')
    assert response.status_code == 200
    assert response.get_json() == "Idea added succefully"

def test_empty_list(client: FlaskClient):
    response = client.get('/favorite/JohnDoe')
    assert response.status_code == 200
    assert response.get_json() == {"ideas": []}

def test_get_user_favorites(client: FlaskClient):
    # Add an idea first to retrieve it later
    client.post('/favorite/JohnDoe/idea_id1')
    client.post('/favorite/JohnDoe/idea_id2')
    response = client.get('/favorite/JohnDoe')
    assert response.status_code == 200
    assert response.get_json() == {"ideas": ["idea_id1", "idea_id2"]}

def test_remove_favorite(client: FlaskClient):
    # Add an idea first, then remove it
    client.post('/favorite/JohnDoe/idea_id1')
    client.post('/favorite/JohnDoe/idea_id2')
    response = client.delete('/favorite/JohnDoe/idea_id1')
    
    assert response.status_code == 200
    assert response.get_json() == "Idea removed succefully"
    
    # Verify that the idea was removed
    response = client.get('/favorite/JohnDoe')
    assert response.status_code == 200
    assert response.get_json() == {"ideas": ["idea_id2"]}

def test_remove_all_favorites(client: FlaskClient):
    # Add an idea first, then remove it
    client.post('/favorite/JohnDoe/idea_id1')
    client.post('/favorite/JohnDoe/idea_id2')
    response = client.delete('/favorite/JohnDoe/idea_id1')
    
    assert response.status_code == 200
    assert response.get_json() == "Idea removed succefully"

    response = client.delete('/favorite/JohnDoe/idea_id2')
    
    assert response.status_code == 200
    assert response.get_json() == "Idea removed succefully"
    
    # Verify that the idea was removed
    response = client.get('/favorite/JohnDoe')
    assert response.status_code == 200
    assert response.get_json() == {"ideas": []}
