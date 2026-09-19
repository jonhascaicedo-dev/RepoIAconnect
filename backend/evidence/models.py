from dataclasses import dataclass, asdict, field

@dataclass
class EvidenceItem:
    title: str
    source: str
    url: str | None = None
    published_at: str | None = None
    evidence_type: str | None = None
    relevance: float | None = None
    supports: list[str] = field(default_factory=list)
    contradicts: list[str] = field(default_factory=list)
    excerpt: str | None = None
    retrieved_at: str | None = None

    def to_dict(self):
        return asdict(self)
