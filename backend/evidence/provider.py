from abc import ABC, abstractmethod
from .models import EvidenceItem

class EvidenceProvider(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[EvidenceItem]:
        raise NotImplementedError

class MockEvidenceProvider(EvidenceProvider):
    def search(self, query: str, limit: int = 5):
        return [EvidenceItem(
            title="Fuente simulada de desarrollo",
            source="mock",
            evidence_type="synthetic",
            relevance=0.0,
            excerpt="Resultado sintético. No utilizar para decisiones clínicas."
        )][:limit]
