import json
import os
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/ai", tags=["ai-gateway"])

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


@router.post("/gateway")
def gateway(payload: dict):
    """Gateway for Mistral structured hypotheses, never definitive diagnosis."""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="MISTRAL_API_KEY no configurada")

    model = os.getenv("MEDICHECK_AI_MODEL", "mistral-small-latest")
    normalized_data = payload.get("normalized_data", {})
    evidence = payload.get("evidence", [])

    request_payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Eres un asistente de apoyo clínico. Genera únicamente hipótesis "
                    "diferenciales, no diagnósticos definitivos, tratamientos ni órdenes médicas. "
                    "Usa solo la información proporcionada. Señala incertidumbre y datos faltantes. "
                    "Devuelve exclusivamente JSON con la estructura solicitada."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "normalized_data": normalized_data,
                        "evidence": evidence,
                        "required_output": {
                            "hypotheses": [
                                {
                                    "name": "string",
                                    "confidence": "number or null",
                                    "supporting_evidence": ["string"],
                                    "contradicting_evidence": ["string"],
                                    "missing_information": ["string"],
                                }
                            ]
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0,
        "max_tokens": 800,
    }

    request = Request(
        MISTRAL_URL,
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=45) as response:
            if response.status < 200 or response.status >= 300:
                raise RuntimeError(f"Mistral HTTP {response.status}")
            body = json.loads(response.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        result = json.loads(content)
        if not isinstance(result, dict) or not isinstance(result.get("hypotheses"), list):
            raise ValueError("Respuesta de Mistral sin esquema hypotheses válido")
        return result
    except (HTTPError, URLError, TimeoutError, socket.timeout, json.JSONDecodeError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=f"Error en proveedor de IA: {type(exc).__name__}") from exc
