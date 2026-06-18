import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage_loads(client):
    """Verify that the user interface loads with a successful HTTP 200 status."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"GreenOps AI" in response.data

def test_calculation_valid_payload(client):
    """Verify the calculation engine accurately computes telemetry data."""
    payload = {
        "name": "Test_User",
        "prompts": 50,
        "hours": 8,
        "storage": 500,
        "optimization": 20
    }
    response = client.post('/calculate', 
                           data=json.dumps(payload), 
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert 'energy' in data
    assert 'co2' in data
    assert 'insights' in data

def test_calculation_invalid_media_type(client):
    """Verify system returns a 415 error code when data content type isn't JSON."""
    response = client.post('/calculate', data="plain text input", content_type='text/plain')
    assert response.status_code == 415
