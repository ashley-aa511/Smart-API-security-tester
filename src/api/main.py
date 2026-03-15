"""
FastAPI Application - Smart API Security Tester
Provides REST endpoints for triggering and retrieving security scans.
"""

import sys
import uuid
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.scanner import SecurityScanner, ScanSession
from src.agents.coordinator_agent import CoordinatorAgent

app = FastAPI(
    title="Smart API Security Tester",
    description="AI-powered API security scanner using OWASP API Security Top 10",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory scan store (replace with Azure Storage for production)
scan_store: Dict[str, dict] = {}


# ─── Request / Response Models ────────────────────────────────────────────────

class ScanRequest(BaseModel):
    target_url: str
    headers: Dict[str, str] = {}
    use_ai_planning: bool = True

class ScanStatus(BaseModel):
    scan_id: str
    status: str
    target_url: str
    started_at: str
    completed_at: Optional[str] = None
    summary: Optional[dict] = None

class ScanResult(BaseModel):
    scan_id: str
    target_url: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    summary: Optional[dict] = None
    results: Optional[List[dict]] = None
    ai_plan: Optional[dict] = None


# ─── Background Scan Runner ───────────────────────────────────────────────────

async def run_scan_background(scan_id: str, target_url: str, headers: Dict, use_ai: bool):
    """Runs a security scan in the background and stores results."""
    try:
        scan_store[scan_id]["status"] = "running"

        ai_plan = None

        # Step 1: AI planning (if enabled and Azure configured)
        if use_ai:
            try:
                coordinator = CoordinatorAgent()
                ai_plan = await coordinator.plan_scan(target_url, headers)
                scan_store[scan_id]["ai_plan"] = ai_plan
            except Exception as e:
                scan_store[scan_id]["ai_plan_error"] = str(e)

        # Step 2: Execute security tests
        scanner = SecurityScanner()
        config = {
            "target_url": target_url,
            "headers": headers,
            "selected_tests": scanner.test_classes,
        }

        loop = asyncio.get_event_loop()
        session: ScanSession = await loop.run_in_executor(None, scanner.run_scan, config)

        scan_store[scan_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "summary": session.summary,
            "results": session.results,
            "ai_plan": ai_plan,
        })

    except Exception as e:
        scan_store[scan_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat(),
        })


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Smart API Security Tester", "version": "1.0.0"}


@app.post("/api/v1/scan", response_model=ScanStatus, status_code=202)
async def create_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Initiate a security scan against a target API.

    The scan runs in the background. Poll GET /api/v1/scan/{scan_id} for results.
    """
    scan_id = str(uuid.uuid4())
    started_at = datetime.now().isoformat()

    scan_store[scan_id] = {
        "scan_id": scan_id,
        "target_url": request.target_url,
        "status": "pending",
        "started_at": started_at,
        "completed_at": None,
        "summary": None,
        "results": None,
        "ai_plan": None,
    }

    background_tasks.add_task(
        run_scan_background,
        scan_id,
        request.target_url,
        request.headers,
        request.use_ai_planning,
    )

    return ScanStatus(
        scan_id=scan_id,
        status="pending",
        target_url=request.target_url,
        started_at=started_at,
    )


@app.get("/api/v1/scan/{scan_id}", response_model=ScanResult)
async def get_scan(scan_id: str):
    """
    Retrieve the status and results of a scan.
    """
    if scan_id not in scan_store:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found.")

    data = scan_store[scan_id]
    return ScanResult(**data)


@app.get("/api/v1/scans")
async def list_scans():
    """List all scans with their statuses."""
    return [
        {
            "scan_id": v["scan_id"],
            "target_url": v["target_url"],
            "status": v["status"],
            "started_at": v["started_at"],
        }
        for v in scan_store.values()
    ]


@app.delete("/api/v1/scan/{scan_id}")
async def delete_scan(scan_id: str):
    """Delete a scan from the store."""
    if scan_id not in scan_store:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found.")
    del scan_store[scan_id]
    return {"message": f"Scan {scan_id} deleted."}


@app.post("/api/v1/plan")
async def plan_scan_only(request: ScanRequest):
    """
    Use the AI Coordinator Agent to generate a scan plan without executing tests.
    Requires Azure OpenAI to be configured.
    """
    try:
        coordinator = CoordinatorAgent()
        plan = await coordinator.plan_scan(request.target_url, request.headers)
        return {"status": "success", "plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI planning failed: {str(e)}")


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
