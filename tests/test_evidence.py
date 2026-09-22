from backend.evidence.engine import EvidenceEngine
from backend.evidence.provider import EvidenceProvider
from backend.evidence.models import EvidenceItem


class FakeEvidenceProvider(EvidenceProvider):
    def search(self, query: str, limit: int = 5):
        return [EvidenceItem(
            title="Test evidence",
            source="test",
            evidence_type="test",
            relevance=1.0,
        )][:limit]


def test_evidence_engine_builds_query_and_returns_items():
    engine = EvidenceEngine(FakeEvidenceProvider())
    query, items = engine.search({
        "symptoms": [{"normalized": "dolor de cabeza"}],
        "examinations": [{"name": "hemoglobina", "value": 13.2}]
    })
    assert "dolor de cabeza" in query
    assert "hemoglobina" in query
    assert len(items) == 1
    assert items[0]["source"] == "test"
