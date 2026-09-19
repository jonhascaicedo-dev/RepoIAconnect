# MediCheck v1.8

Integrated MVP for clinical-case intake and processing.

## Scope
- FastAPI API
- ClinicalCase domain model
- symptom and examination intake
- normalization and basic triage placeholder
- in-memory persistence for development
- Mock AI service
- Evidence Engine with mock provider
- automated tests via GitHub Actions

> Development/MVP only. The system does not provide autonomous medical diagnosis and must not be used with real patient data yet.

## Run locally
```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

API docs: `/docs`
Health: `/health`
