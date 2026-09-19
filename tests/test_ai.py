from backend.ai.factory import build_ai_provider
from backend.ai.http_provider import HTTPAIProvider
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
    assert processed.status.value == "processing"
    assert processed.ai_metadata["synthetic"] is True
    assert processed.hypotheses
    assert any(item["event"] == "ai_analysis_completed" for item in processed.audit)


def test_factory_defaults_to_mock(monkeypatch):
    monkeypatch.delenv("MEDICHECK_AI_PROVIDER", raising=False)
    assert isinstance(build_ai_provider(), MockAIProvider)


def test_http_provider_requires_url(monkeypatch):
    monkeypatch.delenv("MEDICHECK_AI_URL", raising=False)
    try:
        HTTPAIProvider()
    except ValueError as exc:
        assert "MEDICHECK_AI_URL" in str(exc)
    else:
        raise AssertionError("HTTPAIProvider should require MEDICHECK_AI_URL")
