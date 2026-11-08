"""
Project TITAN — FastAPI Backend
REST API server that powers the Streamlit UI and exposes TITAN's capabilities.
"""

from __future__ import annotations

import threading
import time
from typing import Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from backend.config import PROJECTS_DIR, get_available_providers, validate_config
from backend.memory import SessionMemory

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


def _cleanup_old_builds() -> None:
    """Remove completed/failed builds older than 2 hours to prevent memory leaks."""
    import time

    TWO_HOURS = 7200
    while True:
        time.sleep(600)  # Check every 10 minutes
        cutoff = time.time() - TWO_HOURS
        to_delete = [
            bid
            for bid, state in list(_active_builds.items())
            if state.get("status") in ("done", "failed")
            and state.get("_finished_at", 0) < cutoff
        ]
        for bid in to_delete:
            _active_builds.pop(bid, None)
            logger.debug(f"Evicted stale build: {bid}")


_cleanup_thread = threading.Thread(target=_cleanup_old_builds, daemon=True)
_cleanup_thread.start()


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


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    provider: str


class EnhancePromptRequest(BaseModel):
    prompt: str
    target_stack: str = "auto"


COPILOT_SYSTEM_PROMPT = """You are TITAN Copilot — an expert AI Software Architect and autonomous engineering assistant for Project TITAN.
You help users brainstorm software ideas, choose optimal tech stacks, design scalable system architectures, review code, debug build errors, and construct high-impact prompts for Project TITAN's autonomous build engine.

Keep your answers structured, punchy, and technical.
When recommending a project idea or prompt, provide:
1. Short overview
2. Recommended Tech Stack
3. Core Architecture
4. A ready-to-run TITAN Prompt that the user can copy or click to build."""


# ── Endpoints ──────────────────────────────────────────────────────────────


@app.post("/chat", response_model=ChatResponse)
def chat_copilot(req: ChatRequest) -> ChatResponse:
    """TITAN AI Copilot chat for ideation, architecture, debugging, and suggestions."""
    from camel.agents import ChatAgent
    from backend.ai.model_factory import get_gemini_model, get_groq_model

    prompt = req.message
    if req.history:
        ctx = "\n".join([f"{m.role}: {m.content}" for m in req.history[-4:]])
        full_prompt = f"Previous conversation:\n{ctx}\n\nUser: {prompt}"
    else:
        full_prompt = prompt

    # Try Gemini 2.5 Flash first, then Groq
    for provider, model_func in [
        ("gemini", lambda: get_gemini_model("gemini-2.5-flash")),
        ("groq", lambda: get_groq_model("openai/gpt-oss-120b")),
        ("groq", lambda: get_groq_model("qwen/qwen3.8-27b")),
    ]:
        try:
            model = model_func()
            agent = ChatAgent(system_message=COPILOT_SYSTEM_PROMPT, model=model)
            resp = agent.step(full_prompt)
            reply = resp.msgs[0].content
            return ChatResponse(reply=reply, provider=provider)
        except Exception as e:
            logger.warning(f"Copilot chat with {provider} failed: {e}")
            continue

    # Offline / local intelligent fallback
    fallback_reply = (
        f"⚡ **TITAN Copilot**\n\n"
        f"Here is an architecture strategy for *'{req.message}'*:\n\n"
        f"• **Recommended Stack:** FastAPI (Python 3.11) + SQLite/SQLAlchemy + Pydantic v2 + Modern Glassmorphic Dashboard\n"
        f"• **Architecture:** Modular MVC with clear separation between router endpoints, services, and storage models.\n"
        f"• **Security:** JWT authentication, environment-driven secrets, and rate limiting.\n\n"
        f"💡 **Suggested Build Prompt:**\n"
        f"`Build a {req.message} with production-ready REST API, schema validation, unit tests, and interactive UI.`\n\n"
        f"*Click 'Use as Project Prompt' to send this directly to the build engine!*"
    )
    return ChatResponse(reply=fallback_reply, provider="local-fallback")


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

    def progress_handler(event):
        state = _active_builds[build_id]
        state["events"].append(
            {
                "step": event.step,
                "total": event.total,
                "agent": event.agent,
                "action": event.action,
                "message": event.message,
                "status": event.status,
                "file_path": event.file_path,
                "percent": event.percent,
                "timestamp": event.timestamp,
            }
        )
        state["progress"] = event.percent
        state["current_agent"] = event.agent
        state["current_action"] = event.action
        state["status"] = "building"

    def run_build():
        from backend.orchestrator import Orchestrator

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
            _active_builds[build_id]["_finished_at"] = time.time()
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
            _active_builds[build_id]["_finished_at"] = time.time()
            _active_builds[build_id]["result"] = {"success": False, "error": str(e)}

    thread = threading.Thread(target=run_build, daemon=True)
    thread.start()

    return {
        "build_id": build_id,
        "message": f"Build started! Track at /build/{build_id}",
    }


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
    # Deduplicate by name, keeping the latest one
    seen: set[str] = set()
    unique = []
    for p in projects:
        if p.name not in seen:
            seen.add(p.name)
            unique.append(p)
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
            for p in unique
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


@app.get("/projects/{project_name}/files")
def get_project_files(project_name: str) -> dict:
    """List all source files in a project workspace."""
    proj_dir = PROJECTS_DIR / project_name
    if not proj_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")
    files = []
    for p in sorted(proj_dir.rglob("*")):
        if p.is_file():
            parts = p.relative_to(proj_dir).parts
            if any(part in (".git", "__pycache__", "node_modules", ".venv") for part in parts):
                continue
            files.append(str(p.relative_to(proj_dir)))
    return {"files": files}


@app.get("/projects/{project_name}/file")
def get_project_file_content(project_name: str, file_path: str) -> dict:
    """Get the text content of a specific project file."""
    proj_dir = (PROJECTS_DIR / project_name).resolve()
    target = (proj_dir / file_path).resolve()
    if not str(target).startswith(str(proj_dir)):
        raise HTTPException(status_code=403, detail="Path traversal forbidden")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    try:
        content = target.read_text(encoding="utf-8")
        return {"content": content, "size": len(content)}
    except Exception as e:
        return {"content": f"Binary or unreadable file: {e}", "size": 0}


@app.post("/projects/{project_name}/open_vscode")
def open_project_vscode(project_name: str) -> dict:
    """Open project workspace in VS Code."""
    proj_dir = PROJECTS_DIR / project_name
    if not proj_dir.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")
    from backend.controllers.vscode import VSCodeController
    vc = VSCodeController(proj_dir)
    success = vc.open_project()
    return {"success": success}


@app.post("/prompt/enhance")
def enhance_prompt_endpoint(req: EnhancePromptRequest) -> dict:
    """Transform a short idea into an architectural build prompt."""
    prompt_text = req.prompt.strip()
    if not prompt_text:
        return {"enhanced": ""}
    from camel.agents import ChatAgent
    from backend.ai.model_factory import get_groq_model, get_gemini_model
    enhance_sys = (
        "You are TITAN's Principal Systems Architect. Transform the user's brief concept "
        "into a high-impact, production specification for an autonomous AI software build engine. "
        "Detail architecture patterns, database models, REST/GraphQL endpoints, security, and testing. "
        "Return ONLY the enhanced specification prompt starting with 'Build a ...', under 200 words."
    )
    for provider, model_func in [
        ("groq", lambda: get_groq_model("openai/gpt-oss-120b")),
        ("gemini", lambda: get_gemini_model("gemini-2.5-flash")),
    ]:
        try:
            agent = ChatAgent(system_message=enhance_sys, model=model_func())
            res = agent.step(f"Idea: {prompt_text}\nStack focus: {req.target_stack}")
            if res.msgs and res.msgs[0].content:
                return {"enhanced": res.msgs[0].content.strip(), "provider": provider}
        except Exception as e:
            logger.warning(f"Enhance prompt failed with {provider}: {e}")
    return {
        "enhanced": f"Build a {prompt_text} featuring clean modular architecture, relational database persistence, Pydantic schemas, unit tests, and comprehensive OpenAPI documentation.",
        "provider": "fallback",
    }


@app.get("/system/ping_providers")
def ping_providers() -> dict:
    """Ping configured model providers and return live response latency."""
    results = {}
    import time
    from backend.ai.model_factory import get_groq_model, get_gemini_model, get_mistral_model

    # Ping Groq
    t0 = time.time()
    try:
        _ = get_groq_model("openai/gpt-oss-120b")
        results["groq"] = {
            "status": "online",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "model": "openai/gpt-oss-120b",
        }
    except Exception as e:
        results["groq"] = {"status": "error", "error": str(e)}

    # Ping Gemini
    t0 = time.time()
    try:
        _ = get_gemini_model("gemini-2.5-flash")
        results["gemini"] = {
            "status": "online",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "model": "gemini-2.5-flash",
        }
    except Exception as e:
        results["gemini"] = {"status": "error", "error": str(e)}

    # Ping Mistral
    t0 = time.time()
    try:
        _ = get_mistral_model("mistral-small-latest")
        results["mistral"] = {
            "status": "online",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "model": "mistral-small-latest",
        }
    except Exception as e:
        results["mistral"] = {"status": "error", "error": str(e)}

    return {"providers": results}


# ── Run ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("🚀 Starting Project TITAN API...")
    missing = validate_config()
    if missing:
        logger.warning(f"Missing config: {missing}")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
