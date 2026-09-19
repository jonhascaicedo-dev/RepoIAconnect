from backend.domain.clinical_case import ClinicalCase, CaseStatus
from backend.services.case_store import STORE
from backend.services.evidence_service import ClinicalEvidenceService
from backend.ai.worker import AIWorker


def normalize_case(case: ClinicalCase):
    case.normalized_data = {
        "symptoms": [
            {"original": s.name, "normalized": s.normalized_name or s.name.lower().strip(),
             "severity": s.severity, "duration": s.duration, "onset": s.onset}
            for s in case.symptoms
        ],
        "examinations": [
            {"name": e.name, "value": e.value, "unit": e.unit,
             "reference_range": e.reference_range, "date": e.date}
            for e in case.examinations
        ]
    }
    case.add_audit("clinical_normalization", "system")
    return case


def triage_case(case: ClinicalCase):
    # Until a clinically reviewed red-flag ruleset exists, do not infer urgency
    # from symptom severity or from the presence of an examination.
    case.triage = {
        "red_flags": [],
        "urgency": "not_assessed",
        "assessment_status": "pending_clinical_rules",
        "rule_version": "triage-mvp-2"
    }
    case.add_audit("triage_completed", "system", case.triage)
    return case


def start_pipeline(case: ClinicalCase):
    case.transition(CaseStatus.PROCESSING)
    normalize_case(case)
    triage_case(case)
    ClinicalEvidenceService().evaluate_case(case)
    AIWorker().process(case)
    STORE.save(case)
    return case
