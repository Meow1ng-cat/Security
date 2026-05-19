from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_idor_returns_404():
    r = client.get("/files/2", params={"user_id": 1})
    assert r.status_code == 404

def test_owner_can_read():
    r = client.get("/files/1", params={"user_id": 1})
    assert r.status_code == 200

def test_admin_can_read():
    r = client.get("/files/2", params={"user_id": 3})
    assert r.status_code == 200
def test_admin_can_delete():
    before = len(client.get("/files/all", params={"user_id": 3}).json())
    assert before > 0

    r = client.delete("/files/2", params={"user_id": 3})
    assert r.status_code == 200

    after = len(client.get("/files/all", params={"user_id": 3}).json())
    assert after == before - 1