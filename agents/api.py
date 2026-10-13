"""
FastAPI REST API Server for Echo Hemodynamic Agent.
"""
from typing import Dict, Any, List
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")
WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(
    title="Echo Hemodynamic Agent API",
    description="Enterprise Distributed Component Platform (Cardiology & Intensive Care Systems)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/", include_in_schema=False)
def calculator_page():
    return FileResponse(WEB_DIR / "index.html", media_type="text/html")


@app.get("/calculator.js", include_in_schema=False)
def calculator_script():
    return FileResponse(WEB_DIR / "calculator.js", media_type="application/javascript")


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "echo-hemodynamic-agent", "domain": "Cardiology & Intensive Care Systems", "standard": "AHA/ACC Guidelines / Surviving Sepsis Campaign", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=400, detail="Sensitive identifiers are not accepted")
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
