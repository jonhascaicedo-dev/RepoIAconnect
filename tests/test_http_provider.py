import json
import os
from unittest.mock import patch

import pytest

from backend.ai.http_provider import HTTPAIProvider


def test_http_provider_requires_url(monkeypatch):
    monkeypatch.delenv("MEDICHECK_AI_URL", raising=False)
    with pytest.raises(ValueError):
        HTTPAIProvider()


def test_http_provider_parses_hypotheses():
    provider = HTTPAIProvider(url="http://example.test")
    result = provider._parse_hypotheses({
        "hypotheses": [{
            "name": "Hipótesis de prueba",
            "confidence": None,
            "supporting_evidence": ["test"],
            "contradicting_evidence": [],
            "missing_information": ["revisión clínica"],
        }]
    })
    assert len(result) == 1
    assert result[0].name == "Hipótesis de prueba"
    assert result[0].confidence is None


def test_http_provider_retries_and_sends_auth(monkeypatch):
    class FakeResponse:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return json.dumps({"hypotheses": [{"name": "Prueba"}]}).encode()

    calls = []
    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        if len(calls) == 1:
            raise TimeoutError("temporary")
        return FakeResponse()

    monkeypatch.setenv("MEDICHECK_AI_API_KEY", "secret-not-logged")
    provider = HTTPAIProvider(url="http://example.test", retries=1, timeout=5)
    with patch("backend.ai.http_provider.urlopen", fake_urlopen):
        result = provider.analyze({"symptoms": []}, [])

    assert len(calls) == 2
    assert calls[0][1] == 5
    assert calls[0][0].get_header("Authorization") == "Bearer secret-not-logged"
    assert result[0].name == "Prueba"
