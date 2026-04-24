"""
GEO Audit router — /audit endpoints.

POST /audit/run       Run a GEO audit (async, returns job id)
GET  /audit/{id}      Get audit result by id
GET  /audit/list      List audits for authenticated client
"""
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.services.geo_audit import audit_single_company, generate_dynamic_recommendations
from backend.services.pdf_engine import generate_pdf
from backend.db.supabase_client import get_supabase

router = APIRouter(prefix="/audit", tags=["audit"])

# In-memory job store (replace with Supabase polling in Phase 2)
_jobs: dict[str, dict] = {}


class AuditRequest(BaseModel):
    company_name: str
    client_id: str | None = None  # optional; links to authenticated client


class AuditResponse(BaseModel):
    job_id: str
    status: str  # "pending" | "running" | "done" | "error"


def _run_audit(job_id: str, company_name: str, client_id: str | None):
    """Background task: run audit, save to Supabase, generate PDF."""
    _jobs[job_id]["status"] = "running"
    try:
        result = audit_single_company(company_name)
        recs = generate_dynamic_recommendations(result.get("geo_breakdown", {}), company_name)
        pdf_path = generate_pdf(result, recs)

        # Persist to Supabase
        try:
            db = get_supabase()
            row = {
                "id": job_id,
                "client_id": client_id,
                "company_name": company_name,
                "geo_score": result.get("geo_score", 0),
                "breakdown": result.get("geo_breakdown", {}),
                "recommendations": recs,
                "website_url": result.get("website_url"),
                "pdf_path": pdf_path,
            }
            db.table("audits").insert(row).execute()
        except Exception as e:
            print(f"[supabase] insert failed (non-fatal): {e}")

        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["result"] = result
        _jobs[job_id]["recommendations"] = recs
        _jobs[job_id]["pdf_path"] = pdf_path

    except Exception as e:
        _jobs[job_id]["status"] = "error"
        _jobs[job_id]["error"] = str(e)


@router.post("/run", response_model=AuditResponse)
async def start_audit(req: AuditRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "company_name": req.company_name}
    background_tasks.add_task(_run_audit, job_id, req.company_name, req.client_id)
    return AuditResponse(job_id=job_id, status="pending")


@router.get("/{job_id}")
async def get_audit(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        # Try Supabase
        try:
            db = get_supabase()
            resp = db.table("audits").select("*").eq("id", job_id).single().execute()
            if resp.data:
                return {"status": "done", **resp.data}
        except Exception:
            pass
        raise HTTPException(status_code=404, detail="Audit job not found")
    return job
