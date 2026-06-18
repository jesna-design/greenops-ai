import pytest
import json
from server import app

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

def test_calculation_edge_case(client):
    """Verify system performance when inputs are set to zero or minimum values."""
    payload = {
        "name": "Test_User",
        "prompts": 0,
        "hours": 0,
        "storage": 0,
        "optimization": 0
    }
    response = client.post('/calculate', 
                           data=json.dumps(payload), 
                           content_type='application/json')
    assert response.status_code == 200
