from backend.domain.clinical_case import CaseStatus
from backend.services.case_store import STORE
from backend.ai.factory import build_ai_provider


class AIWorker:
    def __init__(self, provider=None):
        self.provider = provider or build_ai_provider()

    def process(self, case):
        case.transition(CaseStatus.AI_REVIEW, actor="ai-worker")
        hypotheses = self.provider.analyze(case.normalized_data, case.evidence)
        metadata = self.provider.metadata()
        case.hypotheses = hypotheses
        case.ai_metadata = metadata
        case.final_result["analysis_status"] = "synthetic" if metadata.get("synthetic") else "external_provider"
        case.add_audit("ai_analysis_completed", "ai-worker", {
            "provider": metadata.get("provider", self.provider.name),
            "hypothesis_count": len(hypotheses),
            "synthetic": bool(metadata.get("synthetic")),
        })
        STORE.save(case)
        return case
