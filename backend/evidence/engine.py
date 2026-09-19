from datetime import datetime, timezone
from .provider import EvidenceProvider

class EvidenceEngine:
    def __init__(self, provider: EvidenceProvider):
        self.provider = provider

    def build_query(self, normalized_case: dict) -> str:
        symptoms = " ".join(x.get("normalized", x.get("original", "")) for x in normalized_case.get("symptoms", []))
        exams = " ".join(f"{x.get('name','')} {x.get('value','')}" for x in normalized_case.get("examinations", []))
        return f"{symptoms} {exams}".strip()

    def search(self, normalized_case: dict, limit: int = 5):
        query = self.build_query(normalized_case)
        items = self.provider.search(query, limit)
        retrieved = datetime.now(timezone.utc).isoformat()
        for item in items:
            item.retrieved_at = retrieved
        return query, [item.to_dict() for item in items]
