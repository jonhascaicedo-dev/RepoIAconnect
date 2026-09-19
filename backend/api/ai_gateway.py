from fastapi import APIRouter

router = APIRouter(prefix="/api/ai", tags=["ai-gateway"])


@router.post("/gateway")
def gateway(payload: dict):
    """Local synthetic gateway implementing the HTTPAIProvider contract.

    Development-only endpoint. It never performs clinical inference.
    """
    symptoms = payload.get("normalized_data", {}).get("symptoms", [])
    symptom_name = "síntoma"
    if symptoms:
        first = symptoms[0]
        symptom_name = first.get("normalized") or first.get("original") or symptom_name

    return {
        "hypotheses": [
            {
                "name": f"Hipótesis sintética vía gateway: {symptom_name}",
                "confidence": None,
                "supporting_evidence": ["local-synthetic-gateway"],
                "contradicting_evidence": [],
                "missing_information": [
                    "evaluación clínica profesional",
                    "historia clínica completa",
                ],
            }
        ]
    }
