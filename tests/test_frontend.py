from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_frontend_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "MediCheck" in response.text
    assert "case-form" in response.text

def test_frontend_assets():
    js = client.get("/frontend/app.js")
    css = client.get("/frontend/styles.css")
    assert js.status_code == 200
    assert css.status_code == 200
    assert "/api/cases" in js.text
