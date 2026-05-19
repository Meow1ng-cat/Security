from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_idor_returns_404():
    response = client.get("/files/2", headers={"X-User-Name": "alice"})
    assert response.status_code == 404

def test_owner_can_read():
    response = client.get("/files/1", headers={"X-User-Name": "alice"})
    assert response.status_code == 200

def test_admin_can_read():
    response = client.get("/files/2", headers={"X-User-Name": "admin"})
    assert response.status_code == 200

def test_admin_can_delete():
    before = client.get("/files/all", headers={"X-User-Name": "admin"}).json()
    assert len(before) > 0

    response = client.delete("/files/2", headers={"X-User-Name": "admin"})
    assert response.status_code == 200

    after = client.get("/files/all", headers={"X-User-Name": "admin"}).json()
    assert len(after) == len(before) - 1