from fastapi import APIRouter, HTTPException
from backend.domain.clinical_case import ClinicalCase, Symptom, Examination
from backend.services.case_store import STORE
from backend.services.clinical_pipeline import start_pipeline

router = APIRouter(prefix="/api/cases", tags=["clinical-cases"])

@router.post("")
def create_case(payload: dict):
    patient_id = str(payload.get("patient_id", "")).strip()
    if not patient_id:
        raise HTTPException(status_code=400, detail="patient_id es requerido")

    symptoms = [Symptom(name=str(x["name"]), severity=x.get("severity"),
                        duration=x.get("duration"), onset=x.get("onset"),
                        normalized_name=x.get("normalized_name"), notes=x.get("notes"))
                for x in payload.get("symptoms", []) if x.get("name")]
    examinations = [Examination(name=str(x["name"]), value=x.get("value"),
                                 unit=x.get("unit"), reference_range=x.get("reference_range"),
                                 date=x.get("date"), source=x.get("source"))
                    for x in payload.get("examinations", []) if x.get("name")]

    case = ClinicalCase(patient_id=patient_id, symptoms=symptoms, examinations=examinations)
    start_pipeline(case)
    return {"case_id": case.id, "status": case.status.value}

@router.get("/{case_id}")
def get_case(case_id: str):
    case = STORE.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return case.to_dict()
