from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api.cases import router as cases_router
from backend.api.ai_gateway import router as ai_gateway_router

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="MediCheck", version="1.8.3")
app.include_router(cases_router)
app.include_router(ai_gateway_router)
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

@app.get("/")
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/health")
def health():
    return {"status": "ok", "service": "medicheck", "version": "1.8.3"}
