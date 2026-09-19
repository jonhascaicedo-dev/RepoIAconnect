from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_and_read_case():
    payload = {
        "patient_id": "demo-patient",
        "symptoms": [{"name": "dolor de cabeza", "severity": "moderate"}],
        "examinations": [{"name": "hemoglobina", "value": 13.2, "unit": "g/dL"}]
    }
    created = client.post("/api/cases", json=payload)
    assert created.status_code == 200
    case_id = created.json()["case_id"]

    fetched = client.get(f"/api/cases/{case_id}")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["status"] == "processing"
    assert body["normalized_data"]["symptoms"][0]["normalized"] == "dolor de cabeza"
