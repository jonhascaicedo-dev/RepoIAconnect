from abc import ABC, abstractmethod
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from .models import EvidenceItem


class EvidenceProvider(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[EvidenceItem]:
        raise NotImplementedError


class PubMedEvidenceProvider(EvidenceProvider):
    """Evidence provider backed by NCBI PubMed E-utilities.

    PubMed E-utilities are public; an API key is optional for low request rates.
    A contact email is required so requests identify the application to NCBI.
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    TOOL = "medicheck"

    def __init__(self, email=None, api_key=None, timeout=15):
        self.email = email or os.getenv("MEDICHECK_EVIDENCE_EMAIL")
        self.api_key = api_key or os.getenv("NCBI_API_KEY")
        self.timeout = timeout
        if not self.email:
            raise ValueError(
                "MEDICHECK_EVIDENCE_EMAIL es requerido para PubMedEvidenceProvider"
            )

    def _request(self, endpoint: str, params: dict) -> bytes:
        query = dict(params)
        query.update({"tool": self.TOOL, "email": self.email})
        if self.api_key:
            query["api_key"] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}?{urlencode(query)}"
        request = Request(url, headers={"Accept": "application/xml"}, method="GET")
        with urlopen(request, timeout=self.timeout) as response:
            return response.read()

    def search(self, query: str, limit: int = 5) -> list[EvidenceItem]:
        limit = max(1, min(int(limit), 10))
        if not query.strip():
            return []

        search_xml = self._request(
            "esearch.fcgi",
            {
                "db": "pubmed",
                "term": query,
                "retmode": "xml",
                "retmax": str(limit),
                "sort": "relevance",
            },
        )
        search_root = ET.fromstring(search_xml)
        pmids = [node.text for node in search_root.findall(".//Id") if node.text]
        if not pmids:
            return []

        fetch_xml = self._request(
            "efetch.fcgi",
            {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml",
            },
        )
        root = ET.fromstring(fetch_xml)
        items = []
        rank = len(pmids)

        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID")
            title = "".join(article.find(".//ArticleTitle").itertext()) if article.find(".//ArticleTitle") is not None else ""
            abstract_parts = ["".join(node.itertext()) for node in article.findall(".//Abstract/AbstractText")]
            excerpt = " ".join(part.strip() for part in abstract_parts if part.strip()) or None
            published = (
                article.findtext(".//PubDate/Year")
                or article.findtext(".//PubDate/MedlineDate")
            )
            if not title or not pmid:
                continue

            items.append(
                EvidenceItem(
                    title=title,
                    source="PubMed",
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    published_at=published,
                    evidence_type="pubmed",
                    relevance=round(1.0 - (len(items) / max(rank, 1)) * 0.1, 3),
                    supports=[],
                    contradicts=[],
                    excerpt=excerpt,
                )
            )

        return items[:limit]


class MockEvidenceProvider(EvidenceProvider):
    """Development-only provider kept for isolated unit tests."""

    def search(self, query: str, limit: int = 5):
        return [
            EvidenceItem(
                title="Fuente simulada de desarrollo",
                source="mock",
                evidence_type="synthetic",
                relevance=0.0,
                excerpt="Resultado sintético. No utilizar para decisiones clínicas.",
            )
        ][:limit]
