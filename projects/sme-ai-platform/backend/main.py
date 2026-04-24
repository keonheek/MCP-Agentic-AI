"""
SME AI Platform — FastAPI backend

Endpoints:
  POST /audit/run        Start a GEO audit (background task)
  GET  /audit/{job_id}   Poll for audit result
  GET  /health           Health check
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.audit import router as audit_router

app = FastAPI(
    title="SME AI Platform",
    description="AI automation services for Korean small businesses",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audit_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sme-ai-platform"}
