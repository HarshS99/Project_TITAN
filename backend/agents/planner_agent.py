"""
Project TITAN — Planner Agent
Uses CAMEL's ChatAgent to decompose a user request (e.g. "Build a Netflix Clone")
into an ordered list of structured tasks that TITAN will execute.

Unlike a single-shot "ask for JSON and hope" prompt, this agent:
- gets a schema-enforced structured output (no hand-rolled regex JSON repair), and
- has a validate_plan tool it can call on its own draft to catch structural
  mistakes (duplicate ids, missing required files, banned commands, mixed
  JS/TS) and fix them before returning a final answer.
"""

from __future__ import annotations

import json
from typing import Any, List, Literal, Optional

from camel.agents import ChatAgent
from camel.toolkits import FunctionTool
from loguru import logger
from pydantic import BaseModel, Field

from backend.ai.model_factory import get_model_by_provider, planner_model

# ---------------------------------------------------------------------------
# Schema — this IS the contract. No more regex-parsing model output against
# rules described only in prose; the model is constrained to this shape.
# ---------------------------------------------------------------------------

TaskType = Literal[
    "create_folder",
    "create_file",
    "write_code",
    "run_command",
    "git_init",
    "git_push",
    "generate_readme",
    "generate_gitignore",
    "open_vscode",
]

AgentName = Literal["planner", "code", "testing", "docs", "terminal", "github", "filesystem"]

# Commands that would start a persistent/blocking server — forbidden per rule 9.
_BANNED_COMMAND_FRAGMENTS = (
    "uvicorn",
    "npm start",
    "npm run dev",
    "python run.py",
    "python app.py",
    "flask run",
    "node server.js",
)


class Task(BaseModel):
    id: int
    type: TaskType
    title: str
    description: str
    agent: AgentName
    file_path: Optional[str] = None
    command: Optional[str] = None
    content: Optional[str] = None


class ProjectPlan(BaseModel):
    project_name: str
    project_description: str
    tech_stack: List[str]
    total_tasks: int
    tasks: List[Task]


class ValidationIssue(BaseModel):
    task_id: Optional[int] = None
    issue: str


class ValidationResult(BaseModel):
    valid: bool
    issues: List[ValidationIssue] = Field(default_factory=list)


PLANNER_SYSTEM_MESSAGE = """You are TITAN's Master Planner — a world-class software architect and AI project manager.

Your job is to take a user's project request and break it down into a precise, ordered list of executable tasks, matching the ProjectPlan schema you have been given.

## Rules
1. Each task must be specific, actionable, and self-contained.
2. Order tasks from foundation to deployment (dependencies first).
3. MAXIMUM 30 tasks total. Be concise. Combine related tasks.
4. DO NOT add tasks to start persistent servers (e.g. uvicorn, npm start, python run.py).
   Only install dependencies, prepare the codebase, and push to Git.
5. File paths are already relative to the project root. DO NOT include the project name
   as a root folder in file paths (e.g. use 'src/main.py', not 'project-name/src/main.py').
6. ALWAYS generate '.vscode/tasks.json' and '.vscode/launch.json' configured to automatically
   install dependencies and start the app when VS Code opens ("runOn": "folderOpen" in tasks.json).
7. If the project uses plain JavaScript (not TypeScript), ALL backend files MUST use .js and
   plain JS syntax — never TypeScript syntax in .js files. Only use .ts if explicitly requested.
8. For Node.js run_command tasks, package.json must consistently use either ES modules
   ("type": "module" + import/export) or CommonJS (require/module.exports) — never both.

## Required workflow
1. Draft a full ProjectPlan covering every file a real developer would need: main files,
   config files, package.json/requirements.txt, .env.example, README, .gitignore, and the
   .vscode files.
2. Your final answer must be a valid JSON matching the ProjectPlan schema.
"""


class PlannerAgent:
    """
    Breaks down a user project request into a structured, validated task plan.

    Structural correctness comes from two places, not a regex-repair fallback:
    - `response_format=ProjectPlan` forces the model's final answer into the schema.
    - The `validate_plan` tool lets the agent check its own draft against the
      planner's hard rules (banned commands, missing required files, mixed
      JS/TS, duplicate ids/paths) and revise before finalizing.
    """

    # Fallback ladder tried in order; each entry is (provider, model_name).
    FALLBACK_MODELS = [
        ("gemini", "gemini-2.5-flash"),
        ("groq", "openai/gpt-oss-120b"),
    ]

    def __init__(self, provider: str | None = None):
        self.provider = provider
        model = get_model_by_provider(provider) if provider else planner_model()
        self._agent = ChatAgent(
            system_message=PLANNER_SYSTEM_MESSAGE,
            model=model,
        )
        logger.info(f"PlannerAgent initialized (provider={provider or 'default'})")

    # ------------------------------------------------------------------
    # Tool exposed to the agent for self-critique
    # ------------------------------------------------------------------

    def validate_plan(self, plan_json: str) -> str:
        """Validate a draft ProjectPlan JSON against TITAN's structural rules.

        Checks for: duplicate task ids, duplicate file_paths, missing
        .vscode/tasks.json or .vscode/launch.json, mixed .ts/.js files,
        and run_command tasks that would start a persistent server.

        Args:
            plan_json: The draft plan, serialized as a JSON string matching
                the ProjectPlan schema (project_name, project_description,
                tech_stack, total_tasks, tasks).

        Returns:
            JSON string: {"valid": bool, "issues": [{"task_id": int|null, "issue": str}]}
        """
        try:
            data = json.loads(plan_json)
        except Exception as exc:
            return ValidationResult(
                valid=False, issues=[ValidationIssue(issue=f"Invalid JSON: {exc}")]
            ).model_dump_json()

        issues: list[ValidationIssue] = []
        tasks = data.get("tasks", [])
        seen_ids: set[Any] = set()
        seen_paths: set[str] = set()
        has_vscode_tasks = False
        has_vscode_launch = False
        extensions_used: set[str] = set()

        for t in tasks:
            tid = t.get("id")
            if tid in seen_ids:
                issues.append(ValidationIssue(task_id=tid, issue="Duplicate task id"))
            seen_ids.add(tid)

            fp = t.get("file_path")
            if fp:
                if fp in seen_paths:
                    issues.append(ValidationIssue(task_id=tid, issue=f"Duplicate file_path: {fp}"))
                seen_paths.add(fp)
                if fp == ".vscode/tasks.json":
                    has_vscode_tasks = True
                if fp == ".vscode/launch.json":
                    has_vscode_launch = True
                if fp.endswith((".ts", ".tsx")):
                    extensions_used.add("ts")
                if fp.endswith((".js", ".jsx")):
                    extensions_used.add("js")

            if t.get("type") == "run_command":
                cmd = (t.get("command") or "").lower()
                for banned in _BANNED_COMMAND_FRAGMENTS:
                    if banned in cmd:
                        issues.append(
                            ValidationIssue(
                                task_id=tid,
                                issue=f"Forbidden persistent-server command '{banned}' (rule 4)",
                            )
                        )

        if not has_vscode_tasks:
            issues.append(ValidationIssue(issue="Missing .vscode/tasks.json (required by rule 6)"))
        if not has_vscode_launch:
            issues.append(ValidationIssue(issue="Missing .vscode/launch.json (required by rule 6)"))
        if {"ts", "js"} <= extensions_used:
            issues.append(
                ValidationIssue(issue="Mixed .ts and .js files in the same plan — pick one (rule 7)")
            )

        return ValidationResult(valid=not issues, issues=issues).model_dump_json()

    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------

    def plan(self, user_request: str, extra_context: str = "") -> dict[str, Any]:
        """
        Takes a natural language project request and returns a structured,
        schema-validated plan as a dict (matching ProjectPlan).
        """
        truncated = user_request[:4000]
        if len(user_request) > 4000:
            truncated += "\n\n[...prompt truncated for planning — full details will be passed to agents per-task...]"

        prompt = f"""
User Request: {truncated}

{f"Additional Context: {extra_context}" if extra_context else ""}

Produce a complete, ordered ProjectPlan. Include ALL files a real developer would need:
main files, config files, package.json/requirements.txt, .env.example, README, .gitignore,
and the required .vscode files. Validate your draft with validate_plan before answering.
"""
        logger.info(f"Planning project: {user_request[:120]}...")

        from backend.ai.model_factory import get_gemini_model, get_groq_model

        last_error: Exception | None = None
        for provider_name, model_name in self.FALLBACK_MODELS:
            try:
                model = (
                    get_groq_model(model_name)
                    if provider_name == "groq"
                    else get_gemini_model(model_name)
                )
                self._agent = ChatAgent(
                    system_message=PLANNER_SYSTEM_MESSAGE,
                    model=model,
                )
                
                current_prompt = prompt
                for _ in range(3):
                    response = self._agent.step(current_prompt, response_format=ProjectPlan)

                    parsed: ProjectPlan | None = getattr(response.msgs[0], "parsed", None)
                    if parsed is None:
                        parsed = ProjectPlan.model_validate_json(response.msgs[0].content)

                    # Validate locally
                    val_result_str = self.validate_plan(parsed.model_dump_json())
                    val_result = ValidationResult.model_validate_json(val_result_str)
                    
                    if val_result.valid:
                        if parsed.tasks:
                            logger.success(
                                f"Plan created via {provider_name}:{model_name} — "
                                f"{parsed.project_name}, {len(parsed.tasks)} tasks"
                            )
                            return parsed.model_dump()
                        break
                    
                    # If invalid, prompt again with issues
                    current_prompt = "Your previous plan had the following issues:\n" + "\n".join([f"- {i.issue}" for i in val_result.issues]) + "\n\nPlease fix them and return the corrected plan."

                logger.warning(f"{provider_name}:{model_name} returned zero tasks or failed validation, trying next model")

            except Exception as exc:
                last_error = exc
                err = str(exc).lower()
                if any(s in err for s in ("429", "rate_limit", "quota", "resource_exhausted")):
                    logger.warning(f"Rate limited on {provider_name}:{model_name}, trying next...")
                else:
                    logger.warning(f"{provider_name}:{model_name} failed: {exc}")
                continue

        logger.error(f"All planner models failed to produce a plan. Last error: {last_error}")
        return ProjectPlan(
            project_name="unnamed-project",
            project_description="Generated project",
            tech_stack=["Python"],
            total_tasks=0,
            tasks=[],
        ).model_dump()

    def reset(self):
        self._agent.reset()