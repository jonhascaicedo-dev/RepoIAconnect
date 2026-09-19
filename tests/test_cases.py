from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "1.8.3"


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
    assert body["status"] == "ai_review"
    assert body["normalized_data"]["symptoms"][0]["normalized"] == "dolor de cabeza"
    assert body["triage"]["urgency"] == "not_assessed"
    assert body["triage"]["assessment_status"] == "pending_clinical_rules"
    assert body["ai_metadata"]["synthetic"] is True
    assert body["hypotheses"]


def test_local_ai_gateway_contract():
    response = client.post(
        "/api/ai/gateway",
        json={
            "model": "local-test",
            "normalized_data": {
                "symptoms": [{"original": "dolor de cabeza", "normalized": "dolor de cabeza"}]
            },
            "evidence": [],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["hypotheses"], list)
    assert body["hypotheses"][0]["confidence"] is None
