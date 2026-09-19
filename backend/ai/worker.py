from backend.domain.clinical_case import CaseStatus
from backend.services.case_store import STORE
from backend.ai.provider import MockAIProvider


class AIWorker:
    def __init__(self, provider=None):
        self.provider = provider or MockAIProvider()

    def process(self, case):
        case.transition(CaseStatus.AI_REVIEW, actor="ai-worker")
        hypotheses = self.provider.analyze(case.normalized_data, case.evidence)
        case.hypotheses = hypotheses
        case.ai_metadata = self.provider.metadata()
        case.final_result["analysis_status"] = "synthetic"
        case.add_audit("ai_analysis_completed", "ai-worker", {
            "provider": self.provider.name,
            "hypothesis_count": len(hypotheses),
            "synthetic": True,
        })
        case.transition(CaseStatus.PROCESSING, actor="ai-worker")
        STORE.save(case)
        return case
