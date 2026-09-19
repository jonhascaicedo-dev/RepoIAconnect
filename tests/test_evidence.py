from backend.evidence.engine import EvidenceEngine
from backend.evidence.provider import MockEvidenceProvider

def test_evidence_engine_builds_query_and_returns_items():
    engine = EvidenceEngine(MockEvidenceProvider())
    query, items = engine.search({
        "symptoms": [{"normalized": "dolor de cabeza"}],
        "examinations": [{"name": "hemoglobina", "value": 13.2}]
    })
    assert "dolor de cabeza" in query
    assert "hemoglobina" in query
    assert len(items) == 1
    assert items[0]["source"] == "mock"
