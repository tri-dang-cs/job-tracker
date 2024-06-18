import uuid

def test_jobs(client):
    response = client.get('/api/jobs')
    assert response.status_code == 200

def test_create_tracker(client):
    response = client.post('/api/tracker', json={'token': 'test', 'keyword': 'python', 'email': 'test@example.com', 'duration': 30})
    assert response.status_code == 200
    data = response.get_json()['data']
    assert 'secret' in data
    assert uuid.UUID(data['secret']).version == 4

def test_view_tracker(client):
    response = client.post('/api/tracker', json={'token': 'test', 'keyword': 'python', 'email': 'test@example.com', 'duration': 30})
    assert response.status_code == 200
    secret = response.get_json()['data']['secret']
    response = client.get(f'/api/tracker/{secret}')
    assert response.status_code == 200
    data = response.get_json()['data']
    assert data['keyword'] == "python"

def test_view_tracker_not_found(client):
    response = client.get('/api/tracker/invalid')
    assert response.status_code == 404

def test_delete_tracker(client):
    response = client.post('/api/tracker', json={'token': 'test', 'keyword': 'python', 'email': 'test@example.com', 'duration': 30})
    assert response.status_code == 200
    secret = response.get_json()['data']['secret']
    response = client.delete(f'/api/tracker/{secret}')
    assert response.status_code == 200
    
def test_delete_tracker_not_found(client):
    response = client.delete('/api/tracker/invalid')
    assert response.status_code == 404