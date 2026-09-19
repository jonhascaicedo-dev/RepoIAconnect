import os

from backend.ai.provider import MockAIProvider
from backend.ai.http_provider import HTTPAIProvider


def build_ai_provider():
    provider = os.getenv("MEDICHECK_AI_PROVIDER", "mock").strip().lower()
    if provider == "http":
        return HTTPAIProvider()
    if provider == "mock":
        return MockAIProvider()
    raise ValueError("MEDICHECK_AI_PROVIDER debe ser 'mock' o 'http'")
