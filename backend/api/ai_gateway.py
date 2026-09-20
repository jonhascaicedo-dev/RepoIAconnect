import json
import os
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/ai", tags=["ai-gateway"])

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
DEFAULT_MODEL = "gemini-3.6-flash"


def _build_prompt(normalized_data: dict, evidence: list) -> str:
    return json.dumps(
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
    )


@router.post("/gateway")
def gateway(payload: dict):
    """Gateway for Gemini structured clinical hypotheses, never definitive diagnosis."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY no configurada")

    model = os.getenv("MEDICHECK_AI_MODEL", DEFAULT_MODEL)
    normalized_data = payload.get("normalized_data", {})
    evidence = payload.get("evidence", [])

    system_prompt = (
        "Eres un asistente de apoyo clínico. Genera únicamente hipótesis diferenciales, "
        "no diagnósticos definitivos, tratamientos ni órdenes médicas. Usa solo la información "
        "proporcionada. Señala incertidumbre y datos faltantes. Devuelve exclusivamente JSON "
        "válido con una clave hypotheses que contenga una lista de objetos con name, confidence, "
        "supporting_evidence, contradicting_evidence y missing_information."
    )
    user_prompt = _build_prompt(normalized_data, evidence)

    request_payload = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": user_prompt}]},
        ],
        "store": False,
    }

    request = Request(
        GEMINI_URL,
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
        outputs = body.get("outputs", [])
        text_parts = [
            part.get("text", "")
            for output in outputs
            if isinstance(output, dict)
            for part in output.get("content", [])
            if isinstance(part, dict) and part.get("type") == "text"
        ]
        content = "".join(text_parts).strip()
        result = json.loads(content)
        if not isinstance(result, dict) or not isinstance(result.get("hypotheses"), list):
            raise ValueError("Respuesta de Gemini sin esquema hypotheses válido")
        return result
    except HTTPError as exc:
        status = exc.code
        if status == 401:
            detail = "Credencial de Gemini inválida"
        elif status == 429:
            detail = "Límite de solicitudes de Gemini alcanzado"
        elif 400 <= status < 500:
            detail = f"Solicitud rechazada por Gemini (HTTP {status})"
        else:
            detail = f"Error temporal de Gemini (HTTP {status})"
        raise HTTPException(status_code=status, detail=detail) from exc
    except (URLError, TimeoutError, socket.timeout) as exc:
        raise HTTPException(status_code=502, detail="No se pudo conectar con Gemini") from exc
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=f"Respuesta de Gemini no válida: {type(exc).__name__}") from exc
