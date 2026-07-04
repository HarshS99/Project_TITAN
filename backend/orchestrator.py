"""
Project TITAN — Master Orchestrator
The central brain that coordinates all agents and controllers
to build complete software projects autonomously.

Flow:
  User Request → Planner → Task Queue → Agent Dispatch → Error Fix → GitHub Push
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from loguru import logger

from backend.agents import PlannerAgent, CodeAgent, TestingAgent, DocsAgent
from backend.controllers import FilesystemController, TerminalController, GitHubController, VSCodeController
from backend.memory import SessionMemory, TaskStatus
from backend.config import PROJECTS_DIR
from backend.mcp_servers.mcp_clients import run_push as github_mcp_push


# ── Progress Event ─────────────────────────────────────────────────────────

@dataclass
class ProgressEvent:
    """Emitted during build for real-time UI updates."""
    step: int
    total: int
    agent: str
    action: str
    message: str
    status: str = "running"  # running | done | error | warning
    file_path: str = ""
    timestamp: float = field(default_factory=time.time)

    @property
    def percent(self) -> int:
        if self.total == 0:
            return 0
        return int((self.step / self.total) * 100)


# ── Build Result ───────────────────────────────────────────────────────────

@dataclass
class BuildResult:
    success: bool
    project_name: str
    project_root: str
    github_url: str = ""
    files_created: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    tasks_completed: int = 0
    tasks_total: int = 0


# ── Orchestrator ───────────────────────────────────────────────────────────

class Orchestrator:
    """
    TITAN's master controller.
    Coordinates all agents and controllers to build projects end-to-end.
    """

    MAX_FIX_ATTEMPTS = 3

    def _call_with_retry(self, func, *args, **kwargs):
        """Helper to run agent tasks with robust rate limit retries and automatic Model Fallback."""
        from backend.agents import CodeAgent, PlannerAgent, TestingAgent, DocsAgent
        
        last_err = None
        
        for attempt in range(6):  # Up to 6 attempts across all providers
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                last_err = exc
                err_str = str(exc).lower()
                if "413" in err_str or "429" in err_str or "rate_limit" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                    # Re-bind the function to a fresh agent initialized with the next provider
                    agent_instance = getattr(func, "__self__", None)
                    if agent_instance:
                        func_name = func.__name__
                        
                        if isinstance(agent_instance, PlannerAgent):
                            providers = ["groq", "gemini", "mistral"]
                            next_provider = providers[(attempt + 1) % 3]
                            logger.warning(f"PlannerAgent rate limited. Fallback to {next_provider} (attempt {attempt+2}/6)...")
                            self._planner = PlannerAgent(provider=next_provider)
                            func = getattr(self._planner, func_name)
                        elif isinstance(agent_instance, CodeAgent):
                            providers = ["groq", "gemini", "mistral"]
                            next_provider = providers[(attempt + 1) % 3]
                            logger.warning(f"CodeAgent rate limited. Fallback to {next_provider} (attempt {attempt+2}/6)...")
                            self._coder = CodeAgent(provider=next_provider)
                            func = getattr(self._coder, func_name)
                        elif isinstance(agent_instance, DocsAgent):
                            providers = ["mistral", "gemini", "groq"]
                            next_provider = providers[(attempt + 1) % 3]
                            logger.warning(f"DocsAgent rate limited. Fallback to {next_provider} (attempt {attempt+2}/6)...")
                            self._docs = DocsAgent(provider=next_provider)
                            func = getattr(self._docs, func_name)
                        elif isinstance(agent_instance, TestingAgent):
                            providers = ["gemini", "groq", "mistral"]
                            next_provider = providers[(attempt + 1) % 3]
                            logger.warning(f"TestingAgent rate limited. Fallback to {next_provider} (attempt {attempt+2}/6)...")
                            self._tester = TestingAgent(provider=next_provider)
                            func = getattr(self._tester, func_name)
                else:
                    raise  # Non-rate-limit error, bubble up immediately
        raise last_err

    def __init__(self, on_progress: Optional[Callable[[ProgressEvent], None]] = None):
        """
        Args:
            on_progress: Optional callback for real-time progress updates.
                         Called with a ProgressEvent on each step.
        """
        self.on_progress = on_progress or (lambda e: None)
        self.memory = SessionMemory()

        # Agents (lazy-initialized per build)
        self._planner: Optional[PlannerAgent] = None
        self._coder: Optional[CodeAgent] = None
        self._tester: Optional[TestingAgent] = None
        self._docs: Optional[DocsAgent] = None

        logger.info("Orchestrator initialized")

    def _init_agents(self):
        """Initialize all agents fresh for a new build, distributing the load across 3 APIs."""
        self._planner = PlannerAgent(provider="groq")
        self._coder = CodeAgent(provider="groq")
        self._tester = TestingAgent(provider="gemini")
        self._docs = DocsAgent(provider="mistral")

    def _emit(self, step: int, total: int, agent: str, action: str, message: str,
              status: str = "running", file_path: str = "") -> None:
        """Emit a progress event."""
        event = ProgressEvent(
            step=step, total=total, agent=agent, action=action,
            message=message, status=status, file_path=file_path
        )
        logger.info(f"[{agent.upper()}] {action}: {message}")
        self.on_progress(event)

    def build(
        self,
        user_request: str,
        auto_push: bool = True,
        auto_open_vscode: bool = True,
        private_repo: bool = False,
        extra_branches: list[str] | None = None,
    ) -> BuildResult:
        """
        Main entry point — build a complete project from a user request.

        Args:
            user_request: Natural language request e.g. "Build a FastAPI todo app"
            auto_push: Whether to push to GitHub after build
            auto_open_vscode: Whether to open VS Code when done
            private_repo: Create a private GitHub repo
            extra_branches: Additional branches to create (default: ['develop'])

        Returns:
            BuildResult with summary of what was done
        """
        start_time = time.time()
        self._init_agents()

        # ── Phase 1: Planning ─────────────────────────────────
        self._emit(0, 1, "planner", "Planning", f"Breaking down: {user_request}")
        plan = self._call_with_retry(self._planner.plan, user_request)

        project_name = self._sanitize_name(plan.get("project_name", "titan-project"))
        description = plan.get("project_description", user_request)
        tech_stack = plan.get("tech_stack", ["Python"])
        tasks = plan.get("tasks", [])
        total = len(tasks) + 3  # +3 for docs, github, vscode phases

        if not tasks:
            logger.error("Planner returned no tasks")
            return BuildResult(
                success=False,
                project_name=project_name,
                project_root="",
                errors=["Planner failed to generate tasks"],
            )

        # ── Phase 2: Setup controllers ────────────────────────
        fs = FilesystemController(project_name)
        terminal = TerminalController(fs.root)
        github = GitHubController(fs.root)
        vscode = VSCodeController(fs.root)

        # Save project to DB
        project_id = self.memory.create_project(
            name=project_name,
            description=description,
            tech_stack=tech_stack,
            total_tasks=len(tasks),
        )

        files_created: list[str] = []
        errors: list[str] = []
        existing_files: dict[str, str] = {}

        # ── Phase 3: Execute tasks ────────────────────────────
        for i, task in enumerate(tasks, 1):
            task_type = task.get("type", "")
            title = task.get("title", f"Task {i}")
            file_path = task.get("file_path", "") or ""
            command = task.get("command", "") or ""
            content = task.get("content", "") or ""

            self._emit(i, total, task.get("agent", "titan"), title, task.get("description", ""),
                       file_path=file_path)

            record_id = self.memory.save_task(project_id, task)
            self.memory.update_task_status(record_id, TaskStatus.IN_PROGRESS)

            try:
                # ── Folder creation ───────────────────────────
                if task_type == "create_folder":
                    fs.create_folder(file_path)
                    self.memory.update_task_status(record_id, TaskStatus.DONE)

                # ── File creation (empty or with content) ─────
                elif task_type == "create_file":
                    fs.create_file(file_path, content)
                    files_created.append(file_path)
                    self.memory.update_task_status(record_id, TaskStatus.DONE)

                # ── Code generation ───────────────────────────
                elif task_type == "write_code":
                    code = self._call_with_retry(
                        self._coder.write_code,
                        file_path=file_path,
                        description=task.get("description", ""),
                        tech_stack=tech_stack,
                        project_context=f"{project_name}: {description[:200]}",
                        existing_files=existing_files,
                    )
                    fs.write_file(file_path, code)
                    existing_files[file_path] = code
                    files_created.append(file_path)
                    self.memory.update_task_status(record_id, TaskStatus.DONE, result=f"{len(code)} chars written")
                    # Small delay between code-gen tasks to stay within TPM limits
                    time.sleep(2)

                # ── Run command ───────────────────────────────
                elif task_type == "run_command":
                    result = terminal.run(command, timeout=120)
                    if not result.success:
                        self._handle_error(result.output, fs, terminal, project_name, description, errors)
                    self.memory.update_task_status(
                        record_id,
                        TaskStatus.DONE if result.success else TaskStatus.FAILED,
                        result=result.stdout,
                        error=result.stderr,
                    )

                # ── Git init ──────────────────────────────────
                elif task_type == "git_init":
                    github.git_init()
                    self.memory.update_task_status(record_id, TaskStatus.DONE)

                # ── README generation ─────────────────────────
                elif task_type == "generate_readme":
                    readme = self._call_with_retry(
                        self._docs.generate_readme,
                        project_name=project_name,
                        description=description,
                        tech_stack=tech_stack,
                        features=self._extract_features(tasks),
                        github_username=github.username,
                        repo_name=project_name,
                    )
                    fs.write_file("README.md", readme)
                    files_created.append("README.md")
                    self.memory.update_task_status(record_id, TaskStatus.DONE)

                # ── .gitignore generation ─────────────────────
                elif task_type == "generate_gitignore":
                    gitignore = self._call_with_retry(self._docs.generate_gitignore, tech_stack)
                    fs.write_file(".gitignore", gitignore)
                    files_created.append(".gitignore")
                    self.memory.update_task_status(record_id, TaskStatus.DONE)

                # ── Git push ──────────────────────────────────
                elif task_type == "git_push" and auto_push:
                    # Handled in Phase 4
                    self.memory.update_task_status(record_id, TaskStatus.SKIPPED,
                                                    result="Handled in GitHub phase")

                else:
                    self.memory.update_task_status(record_id, TaskStatus.SKIPPED)

            except Exception as e:
                error_msg = f"Task '{title}' failed: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
                self.memory.update_task_status(record_id, TaskStatus.FAILED, error=str(e))

            self.memory.increment_completed_tasks(project_id)

        # ── Phase 4: Generate docs if not already done ────────
        step = len(tasks) + 1
        if "README.md" not in files_created:
            self._emit(step, total, "docs", "Generating README", "Writing professional README.md")
            readme = self._call_with_retry(
                self._docs.generate_readme,
                project_name=project_name,
                description=description,
                tech_stack=tech_stack,
                features=self._extract_features(tasks),
                github_username=github.username,
                repo_name=project_name,
            )
            fs.write_file("README.md", readme)
            files_created.append("README.md")

        if ".gitignore" not in files_created:
            gitignore = self._call_with_retry(self._docs.generate_gitignore, tech_stack)
            fs.write_file(".gitignore", gitignore)
            files_created.append(".gitignore")

        # ── Phase 5: GitHub push (via official GitHub MCP Server) ─────────
        github_url = ""
        if auto_push:
            step = len(tasks) + 2
            self._emit(step, total, "github", "Pushing to GitHub",
                       f"Creating repo and pushing {len(files_created)} files via MCP...")
            try:
                gh_result = github_mcp_push(
                    project_root=str(fs.root),
                    repo_name=project_name,
                    description=description,
                    private=private_repo,
                    branches=extra_branches or ["main"],
                )
                github_url = gh_result.get("repo_url", "")
                if gh_result.get("errors"):
                    errors.extend(gh_result["errors"])
                if not gh_result.get("success"):
                    logger.warning(f"GitHub MCP push incomplete: {gh_result['errors']}")
            except Exception as e:
                errors.append(f"GitHub MCP push failed: {e}")
                logger.error(f"GitHub push error: {e}")

            self.memory.update_project_status(project_id, "done", github_url=github_url)
            self._emit(step, total, "github", "GitHub Done",
                       f"✅ Pushed! {github_url}" if github_url else "⚠️ Push had errors",
                       status="done" if github_url else "warning")

        # ── Phase 6: Open VS Code ─────────────────────────────
        if auto_open_vscode:
            step = len(tasks) + 3
            self._emit(step, total, "vscode", "Opening VS Code", str(fs.root))
            vscode.open_project()

        duration = time.time() - start_time
        logger.success(f"🎉 Build complete: {project_name} in {duration:.1f}s")

        return BuildResult(
            success=True,
            project_name=project_name,
            project_root=str(fs.root),
            github_url=github_url,
            files_created=files_created,
            errors=errors,
            duration_seconds=duration,
            tasks_completed=len(tasks),
            tasks_total=len(tasks),
        )

    # ── Helpers ────────────────────────────────────────────────

    def _sanitize_name(self, name: str) -> str:
        """Convert project name to a safe directory/repo name."""
        name = name.lower().strip()
        name = re.sub(r"[^a-z0-9\-_]", "-", name)
        name = re.sub(r"-+", "-", name)
        return name.strip("-") or "titan-project"

    def _extract_features(self, tasks: list[dict]) -> list[str]:
        """Extract a list of features from task titles."""
        features = []
        for task in tasks:
            if task.get("type") == "write_code":
                title = task.get("title", "")
                if title:
                    features.append(title)
        return features[:10]  # Top 10

    def _handle_error(
        self,
        error_output: str,
        fs: FilesystemController,
        terminal: TerminalController,
        project_name: str,
        description: str,
        errors: list[str],
    ) -> None:
        """Attempt to auto-fix errors from terminal output."""
        for attempt in range(self.MAX_FIX_ATTEMPTS):
            logger.warning(f"Auto-fix attempt {attempt + 1}/{self.MAX_FIX_ATTEMPTS}")
            
            # Use retry wrapper so rate limits don't crash the error handler
            diagnosis = self._call_with_retry(
                self._tester.diagnose,
                terminal_output=error_output,
                project_context=f"{project_name}: {description}",
                file_contents=fs.get_project_contents(max_files=5),
            )
            if not diagnosis.has_error:
                break

            # Run fix commands
            for cmd in diagnosis.commands_to_run:
                terminal.run(cmd, timeout=120)

            # Fix files
            for file_fix in diagnosis.files_to_fix:
                fpath = file_fix.get("file_path", "")
                if fpath and fs.file_exists(fpath):
                    current = fs.read_file(fpath)
                    fixed = self._call_with_retry(
                        self._coder.fix_code,
                        file_path=fpath, 
                        current_code=current, 
                        error_message=error_output
                    )
                    fs.write_file(fpath, fixed)

            if attempt == self.MAX_FIX_ATTEMPTS - 1:
                errors.append(f"Could not auto-fix error after {self.MAX_FIX_ATTEMPTS} attempts")
