from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid

class CaseStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    PROCESSING = "processing"
    AI_REVIEW = "ai_review"
    CLINICAL_REVIEW = "clinical_review"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Symptom:
    name: str
    normalized_name: str | None = None
    severity: str | None = None
    duration: str | None = None
    onset: str | None = None
    notes: str | None = None

@dataclass
class Examination:
    name: str
    value: str | float | int | None = None
    unit: str | None = None
    reference_range: str | None = None
    date: str | None = None
    source: str | None = None

@dataclass
class ClinicalHypothesis:
    name: str
    confidence: float | None = None
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)

@dataclass
class ClinicalCase:
    patient_id: str
    symptoms: list[Symptom] = field(default_factory=list)
    examinations: list[Examination] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: CaseStatus = CaseStatus.DRAFT
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    normalized_data: dict = field(default_factory=dict)
    triage: dict = field(default_factory=dict)
    hypotheses: list[ClinicalHypothesis] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    ai_metadata: dict = field(default_factory=dict)
    clinical_review: dict = field(default_factory=dict)
    final_result: dict = field(default_factory=dict)
    audit: list[dict] = field(default_factory=list)

    def transition(self, status: CaseStatus, actor: str = "system"):
        previous = self.status.value
        self.status = status
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.audit.append({
            "timestamp": self.updated_at,
            "event": "status_change",
            "actor": actor,
            "metadata": {"from": previous, "to": status.value}
        })

    def add_audit(self, event: str, actor: str, metadata=None):
        self.audit.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "actor": actor,
            "metadata": metadata or {}
        })

    def to_dict(self):
        return asdict(self)
