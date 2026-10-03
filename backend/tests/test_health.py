import pytest

def test_health_endpoint(client):
    """Test the /api/v1/health endpoint."""
    response = client.get('/api/v1/health')
    
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert json_data['success'] is True
    assert json_data['message'] == "Backend is running"
    assert 'data' in json_data

def test_db_health_endpoint(client, monkeypatch):
    """Test the /api/v1/health/db endpoint."""
    
    # We mock the ping method so it doesn't fail if MongoDB isn't running locally
    # during the test suite execution. A real connection would require a test db setup.
    def mock_ping():
        return True
        
    from app.extensions import mongo
    monkeypatch.setattr(mongo, "ping", mock_ping)
    
    response = client.get('/api/v1/health/db')
    
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert json_data['success'] is True
    assert json_data['message'] == "Database connection successful"
    assert 'database' in json_data['data']
