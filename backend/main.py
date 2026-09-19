from fastapi import FastAPI
from backend.api.cases import router as cases_router

app = FastAPI(title="MediCheck", version="1.8.0")
app.include_router(cases_router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "medicheck", "version": "1.8.0"}
