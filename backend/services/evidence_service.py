from backend.evidence.engine import EvidenceEngine
from backend.evidence.provider import MockEvidenceProvider

class ClinicalEvidenceService:
    def __init__(self, engine=None):
        self.engine = engine or EvidenceEngine(MockEvidenceProvider())

    def evaluate_case(self, case):
        query, evidence = self.engine.search(case.normalized_data)
        case.evidence = evidence
        case.final_result["evidence_query"] = query
        case.add_audit("evidence_retrieved", "system", {
            "count": len(evidence),
            "provider": type(self.engine.provider).__name__
        })
        return case
