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
    assert response.get_json() == "Idea marked succefully"

def test_empty_list(client: FlaskClient):
    response = client.get('/user_favorite/JohnDoe')
    assert response.status_code == 200
    assert response.get_json() == {"ideas": []}

    response = client.get("/idea_count/NonExistIdea")

    assert response.status_code == 200
    assert response.get_json() == {"count": 0}


def test_get_favorites(client: FlaskClient):
    # Add an idea first to retrieve it later
    client.post('/favorite/JohnDoe/idea_id1')
    client.post('/favorite/JohnDoe/idea_id2')
    client.post('/favorite/MarkDean/idea_id2')

    response = client.get('/user_favorite/JohnDoe')
    assert response.status_code == 200
    assert response.get_json() == {"ideas": ["idea_id1", "idea_id2"]}

    response = client.get("/idea_count/idea_id2")
    assert response.status_code == 200

    assert response.get_json()["count"] == 2

    response = client.get("/idea_count/idea_id1")
    assert response.status_code == 200

    assert response.get_json()["count"] == 1



def test_remove_favorite_for_non_exist_user(client: FlaskClient):
    response = client.delete('/favorite/JohnDoe/idea_id1')

    assert response.status_code == 200
    assert response.get_json() == "Idea unmarked succefully"

def test_remove_favorite(client: FlaskClient):
    # Add an idea first, then remove it
    client.post('/favorite/JohnDoe/idea_id1')
    client.post('/favorite/JohnDoe/idea_id2')
    response = client.delete('/favorite/JohnDoe/idea_id1')
    
    assert response.status_code == 200
    assert response.get_json() == "Idea unmarked succefully"
    
    # Verify that the idea was removed
    response = client.get('/user_favorite/JohnDoe')
    assert response.status_code == 200
    assert response.get_json() == {"ideas": ["idea_id2"]}

    response = client.get("/idea_count/idea_id1")

    assert response.status_code == 200
    assert response.get_json()["count"] == 0

def test_remove_all_favorites(client: FlaskClient):
    # Add an idea first, then remove it
    client.post('/favorite/JohnDoe/idea_id1')
    client.post('/favorite/JohnDoe/idea_id2')
    response = client.delete('/favorite/JohnDoe/idea_id1')
    
    assert response.status_code == 200
    assert response.get_json() == "Idea unmarked succefully"

    response = client.delete('/favorite/JohnDoe/idea_id2')
    
    assert response.status_code == 200
    assert response.get_json() == "Idea unmarked succefully"
    
    # Verify that the idea was removed
    response = client.get('/user_favorite/JohnDoe')
    assert response.status_code == 200
    assert response.get_json() == {"ideas": []}

    response = client.get("/idea_count/idea_id1")

    assert response.status_code == 200
    assert response.get_json()["count"] == 0

    response = client.get("/idea_count/idea_id2")

    assert response.status_code == 200
    assert response.get_json()["count"] == 0
