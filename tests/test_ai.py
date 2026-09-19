from backend.ai.provider import MockAIProvider
from backend.ai.worker import AIWorker
from backend.domain.clinical_case import ClinicalCase, Symptom


def test_mock_ai_provider_is_synthetic():
    case = ClinicalCase(patient_id="demo", symptoms=[Symptom(name="dolor de cabeza")])
    case.normalized_data = {"symptoms": [{"original": "dolor de cabeza", "normalized": "dolor de cabeza"}]}
    hypotheses = MockAIProvider().analyze(case.normalized_data, [])
    assert len(hypotheses) == 1
    assert hypotheses[0].confidence is None
    assert "evaluación clínica profesional" in hypotheses[0].missing_information


def test_ai_worker_records_audit_and_metadata():
    case = ClinicalCase(patient_id="demo", symptoms=[Symptom(name="dolor de cabeza")])
    case.normalized_data = {"symptoms": [{"original": "dolor de cabeza", "normalized": "dolor de cabeza"}]}
    processed = AIWorker().process(case)
    assert processed.status.value == "ai_review"
    assert processed.ai_metadata["synthetic"] is True
    assert processed.hypotheses
    assert any(item["event"] == "ai_analysis_completed" for item in processed.audit)
