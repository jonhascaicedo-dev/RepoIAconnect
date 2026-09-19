from dataclasses import asdict
from backend.domain.clinical_case import ClinicalHypothesis


class MockAIProvider:
    """Development-only provider. It never makes a clinical diagnosis."""

    name = "MockAIProvider"
    version = "mock-1"

    def analyze(self, normalized_data: dict, evidence: list[dict]) -> list[ClinicalHypothesis]:
        symptoms = normalized_data.get("symptoms", [])
        if not symptoms:
            return []

        symptom_name = symptoms[0].get("normalized") or symptoms[0].get("original") or "síntoma"
        return [
            ClinicalHypothesis(
                name=f"Hipótesis sintética para: {symptom_name}",
                confidence=None,
                supporting_evidence=["synthetic-development-input"],
                contradicting_evidence=[],
                missing_information=["evaluación clínica profesional", "historia clínica completa"],
            )
        ]

    def metadata(self) -> dict:
        return {"provider": self.name, "version": self.version, "synthetic": True}
