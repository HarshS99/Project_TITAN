"""
Project TITAN — Central Configuration
Loads all environment variables and exposes them as typed constants.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

# ── AI API Keys ──────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
SCRAPEGRAPH_API_KEY: str = os.getenv("SCRAPEGRAPH_API_KEY", "")

# ── GitHub ────────────────────────────────────────────────────
GITHUB_TOKEN: str = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
GITHUB_USERNAME: str = os.getenv("GITHUB_USERNAME", "")

# ── Model Configuration ───────────────────────────────────────
DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER", "groq")
DEFAULT_GROQ_MODEL: str = os.getenv("DEFAULT_GROQ_MODEL", "llama-3.3-70b-versatile")

# Agent → model mapping (must stay in sync with orchestrator._init_agents())
AGENT_MODELS = {
    "planner": {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.2,
        "description": "Plans projects into ordered task lists",
    },
    "code": {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.1,
        "description": "Writes production-quality code",
    },
    "testing": {
        "provider": "gemini",
        "model": "gemini-3.8-flash",
        "temperature": 0.0,
        "description": "Runs tests and fixes errors",
    },
    "docs": {
        "provider": "mistral",
        "model": "mistral-small-latest",
        "temperature": 0.3,
        "description": "Generates README, docs, and GitHub files",
    },
}

# ── Directories ───────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent
# Save projects to the configured directory (defaults to projects/ inside the repo)
_projects_dir_env = os.getenv("TITAN_PROJECTS_DIR", "projects")
PROJECTS_DIR = Path(_projects_dir_env)
if not PROJECTS_DIR.is_absolute():
    PROJECTS_DIR = ROOT_DIR / PROJECTS_DIR

_logs_dir_env = os.getenv("TITAN_LOGS_DIR", "logs")
LOGS_DIR = Path(_logs_dir_env)
if not LOGS_DIR.is_absolute():
    LOGS_DIR = ROOT_DIR / LOGS_DIR

DB_PATH = ROOT_DIR / "titan_memory.db"

# Ensure directories exist
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def validate_config() -> list[str]:
    """Returns a list of missing critical config values."""
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not GITHUB_TOKEN:
        missing.append("GITHUB_PERSONAL_ACCESS_TOKEN")
    return missing


def get_available_providers() -> list[str]:
    """Returns list of providers that have API keys configured."""
    providers = []
    if GROQ_API_KEY:
        providers.append("groq")
    if GEMINI_API_KEY:
        providers.append("gemini")
    if MISTRAL_API_KEY:
        providers.append("mistral")
    if OPENAI_API_KEY:
        providers.append("openai")
    return providers
