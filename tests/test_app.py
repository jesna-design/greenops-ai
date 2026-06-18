import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage(client):
    """Test if the homepage loads successfully"""
    rv = client.get('/')
    assert rv.status_code == 200

def test_calculation_route_exists(client):
    """Test if the main application path functions"""
    # Simple check to verify routing structure aligns with requirements
    assert app.view_functions['home'] is not None
