"""
Project TITAN — FastAPI Backend
REST API server that powers the Streamlit UI and exposes TITAN's capabilities.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Optional

import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.config import validate_config, get_available_providers, PROJECTS_DIR
from backend.orchestrator import Orchestrator, ProgressEvent, BuildResult
from backend.memory import SessionMemory
from loguru import logger

# ── App setup ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Project TITAN API",
    description="🤖 AI Desktop Commander — Build complete software projects autonomously",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = SessionMemory()

# Active builds: {build_id: {"status": ..., "events": [...], "result": ...}}
_active_builds: dict[str, dict] = {}


# ── Request/Response Models ────────────────────────────────────────────────

class BuildRequest(BaseModel):
    request: str
    auto_push: bool = True
    auto_open_vscode: bool = True
    private_repo: bool = False
    extra_branches: list[str] = ["develop"]


class BuildStatusResponse(BaseModel):
    build_id: str
    status: str
    progress: int
    current_agent: str
    current_action: str
    events_count: int
    result: Optional[dict] = None


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "Project TITAN",
        "version": "1.0.0",
        "status": "online",
        "providers": get_available_providers(),
        "missing_config": validate_config(),
    }


@app.get("/health")
def health():
    missing = validate_config()
    return {
        "healthy": len(missing) == 0,
        "missing_config": missing,
        "providers": get_available_providers(),
        "projects_dir": str(PROJECTS_DIR),
    }


@app.post("/build")
def start_build(req: BuildRequest, background_tasks: BackgroundTasks) -> dict:
    """Start a new project build. Returns a build_id to track progress."""
    import uuid
    build_id = str(uuid.uuid4())[:8]
    _active_builds[build_id] = {
        "status": "starting",
        "events": [],
        "progress": 0,
        "current_agent": "planner",
        "current_action": "Initializing...",
        "result": None,
    }

    def progress_handler(event: ProgressEvent):
        state = _active_builds[build_id]
        state["events"].append({
            "step": event.step,
            "total": event.total,
            "agent": event.agent,
            "action": event.action,
            "message": event.message,
            "status": event.status,
            "file_path": event.file_path,
            "percent": event.percent,
            "timestamp": event.timestamp,
        })
        state["progress"] = event.percent
        state["current_agent"] = event.agent
        state["current_action"] = event.action
        state["status"] = "building"

    def run_build():
        try:
            orchestrator = Orchestrator(on_progress=progress_handler)
            result = orchestrator.build(
                user_request=req.request,
                auto_push=req.auto_push,
                auto_open_vscode=req.auto_open_vscode,
                private_repo=req.private_repo,
                extra_branches=req.extra_branches,
            )
            _active_builds[build_id]["status"] = "done" if result.success else "failed"
            _active_builds[build_id]["progress"] = 100
            _active_builds[build_id]["result"] = {
                "success": result.success,
                "project_name": result.project_name,
                "project_root": result.project_root,
                "github_url": result.github_url,
                "files_created": result.files_created,
                "errors": result.errors,
                "duration_seconds": round(result.duration_seconds, 1),
                "tasks_completed": result.tasks_completed,
            }
        except Exception as e:
            logger.error(f"Build {build_id} crashed: {e}")
            _active_builds[build_id]["status"] = "failed"
            _active_builds[build_id]["result"] = {"success": False, "error": str(e)}

    thread = threading.Thread(target=run_build, daemon=True)
    thread.start()

    return {"build_id": build_id, "message": f"Build started! Track at /build/{build_id}"}


@app.get("/build/{build_id}")
def get_build_status(build_id: str) -> BuildStatusResponse:
    """Get current status and progress of a build."""
    if build_id not in _active_builds:
        raise HTTPException(status_code=404, detail="Build not found")
    state = _active_builds[build_id]
    return BuildStatusResponse(
        build_id=build_id,
        status=state["status"],
        progress=state["progress"],
        current_agent=state["current_agent"],
        current_action=state["current_action"],
        events_count=len(state["events"]),
        result=state.get("result"),
    )


@app.get("/build/{build_id}/events")
def get_build_events(build_id: str, since: int = 0) -> dict:
    """Get all events for a build, optionally from a given index."""
    if build_id not in _active_builds:
        raise HTTPException(status_code=404, detail="Build not found")
    events = _active_builds[build_id]["events"][since:]
    return {"events": events, "total": len(_active_builds[build_id]["events"])}


@app.get("/projects")
def list_projects() -> dict:
    """List all projects built by TITAN."""
    projects = memory.list_projects()
    return {
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "status": p.status,
                "github_url": p.github_url,
                "created_at": p.created_at,
                "completed_tasks": p.completed_tasks,
                "total_tasks": p.total_tasks,
            }
            for p in projects
        ]
    }


@app.get("/config")
def get_config() -> dict:
    """Return current configuration status."""
    return {
        "providers": get_available_providers(),
        "missing": validate_config(),
        "projects_dir": str(PROJECTS_DIR),
    }


# ── Run ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("🚀 Starting Project TITAN API...")
    missing = validate_config()
    if missing:
        logger.warning(f"Missing config: {missing}")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
