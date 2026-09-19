import json
import os
from urllib.request import Request, urlopen

from backend.domain.clinical_case import ClinicalHypothesis


class HTTPAIProvider:
    """Adapter for an external AI gateway returning MediCheck's hypothesis schema.

    Required environment variables when enabled:
      MEDICHECK_AI_URL
    Optional:
      MEDICHECK_AI_API_KEY
      MEDICHECK_AI_MODEL

    The gateway must return JSON with a `hypotheses` array. The adapter keeps
    provider-specific details outside the clinical pipeline.
    """

    name = "HTTPAIProvider"
    version = "http-1"

    def __init__(self, url=None, api_key=None, model=None, timeout=30):
        self.url = url or os.getenv("MEDICHECK_AI_URL")
        self.api_key = api_key or os.getenv("MEDICHECK_AI_API_KEY")
        self.model = model or os.getenv("MEDICHECK_AI_MODEL", "default")
        self.timeout = timeout
        if not self.url:
            raise ValueError("MEDICHECK_AI_URL es requerido para HTTPAIProvider")

    def analyze(self, normalized_data: dict, evidence: list[dict]) -> list[ClinicalHypothesis]:
        payload = {
            "model": self.model,
            "normalized_data": normalized_data,
            "evidence": evidence,
            "task": "Generate differential hypotheses only; do not provide a definitive diagnosis or treatment."
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = Request(self.url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))

        hypotheses = body.get("hypotheses", [])
        if not isinstance(hypotheses, list):
            raise ValueError("La respuesta de IA debe contener hypotheses como lista")

        result = []
        for item in hypotheses:
            if not isinstance(item, dict) or not item.get("name"):
                continue
            result.append(ClinicalHypothesis(
                name=str(item["name"]),
                confidence=item.get("confidence"),
                supporting_evidence=list(item.get("supporting_evidence", [])),
                contradicting_evidence=list(item.get("contradicting_evidence", [])),
                missing_information=list(item.get("missing_information", [])),
            ))
        return result

    def metadata(self) -> dict:
        return {
            "provider": self.name,
            "version": self.version,
            "model": self.model,
            "synthetic": False,
        }
