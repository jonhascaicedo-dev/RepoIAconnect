import json
import os
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from backend.domain.clinical_case import ClinicalHypothesis


class HTTPAIProvider:
    """Adapter for an external AI gateway using MediCheck's hypothesis schema.

    The provider never turns an external response into a definitive diagnosis.
    Credentials are read only from environment variables.
    """

    name = "HTTPAIProvider"
    version = "http-1.1"

    def __init__(self, url=None, api_key=None, model=None, timeout=30, retries=1):
        self.url = url or os.getenv("MEDICHECK_AI_URL")
        self.api_key = api_key or os.getenv("MEDICHECK_AI_API_KEY")
        self.model = model or os.getenv("MEDICHECK_AI_MODEL", "default")
        self.timeout = timeout
        self.retries = max(0, int(retries))
        if not self.url:
            raise ValueError("MEDICHECK_AI_URL es requerido para HTTPAIProvider")

    def analyze(self, normalized_data: dict, evidence: list[dict]) -> list[ClinicalHypothesis]:
        payload = {
            "model": self.model,
            "normalized_data": normalized_data,
            "evidence": evidence,
            "task": "Generate differential hypotheses only; do not provide a definitive diagnosis or treatment.",
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        last_error = None
        for attempt in range(self.retries + 1):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    if response.status < 200 or response.status >= 300:
                        raise RuntimeError(f"AI gateway HTTP {response.status}")
                    body = json.loads(response.read().decode("utf-8"))
                return self._parse_hypotheses(body)
            except (HTTPError, URLError, TimeoutError, socket.timeout, json.JSONDecodeError, ValueError, RuntimeError) as exc:
                last_error = exc
                if attempt >= self.retries:
                    break

        raise RuntimeError(f"Error al consultar AI gateway: {last_error}") from last_error

    @staticmethod
    def _parse_hypotheses(body: dict) -> list[ClinicalHypothesis]:
        if not isinstance(body, dict):
            raise ValueError("La respuesta de IA debe ser un objeto JSON")
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
