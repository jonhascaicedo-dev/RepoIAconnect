from backend.domain.clinical_case import ClinicalCase, CaseStatus
from backend.services.case_store import STORE

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
    case.triage = {"red_flags": [], "urgency": "routine", "rule_version": "triage-mvp-1"}
    case.add_audit("triage_completed", "system", case.triage)
    return case

def start_pipeline(case: ClinicalCase):
    case.transition(CaseStatus.PROCESSING)
    normalize_case(case)
    triage_case(case)
    STORE.save(case)
    return case
