from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_bot_start():
    response = client.post("/api/paper/bot/start")
    assert response.status_code == 200
    assert response.json()["running"] == True

def test_bot_status():
    # Make sure it's running from previous test or just check structure
    response = client.get("/api/paper/bot/status")
    assert response.status_code == 200
    assert "running" in response.json()

def test_bot_stop():
    response = client.post("/api/paper/bot/stop")
    assert response.status_code == 200
    assert response.json()["running"] == False
    
    status = client.get("/api/paper/bot/status")
    assert status.json()["running"] == False
