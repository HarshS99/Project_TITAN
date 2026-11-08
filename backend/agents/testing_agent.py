"""
Project TITAN — Testing Agent
Uses CAMEL's ChatAgent to analyze terminal errors, diagnose root causes,
and suggest precise code fixes.

The previous version was handed a pre-truncated dict of "relevant" files
chosen by the caller and had to guess at everything else (e.g. whether a
package genuinely needs installing). This version gets tools to look for
itself: it can read the actual files referenced in a traceback, and check
requirements.txt / package.json / pyproject.toml before recommending an
install, instead of pattern-matching the error text alone.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal, Optional

from camel.agents import ChatAgent
from camel.toolkits import FunctionTool
from loguru import logger
from pydantic import BaseModel, Field

from backend.ai.model_factory import get_model_by_provider, testing_model

# ---------------------------------------------------------------------------
# Schema for the model's structured output (used with response_format).
# ---------------------------------------------------------------------------

ErrorType = Literal[
    "import_error", "syntax_error", "runtime_error", "missing_dep", "config_error", "other"
]
FixType = Literal["edit_code", "install_package", "create_file", "run_command"]
Confidence = Literal["high", "medium", "low"]


class FileFix(BaseModel):
    file_path: str
    fix_description: str
    fix_type: FixType


class Diagnosis(BaseModel):
    has_error: bool
    error_type: ErrorType
    error_summary: str
    files_to_fix: List[FileFix] = Field(default_factory=list)
    commands_to_run: List[str] = Field(default_factory=list)
    confidence: Confidence


# ---------------------------------------------------------------------------
# Public return type — kept as a dataclass so existing callers of
# TestingAgent().diagnose(...) don't need to change.
# ---------------------------------------------------------------------------


@dataclass
class DiagnosisResult:
    has_error: bool
    error_type: str
    error_summary: str
    files_to_fix: list[dict]
    commands_to_run: list[str]
    confidence: str

    @classmethod
    def from_diagnosis(cls, d: Diagnosis) -> "DiagnosisResult":
        return cls(
            has_error=d.has_error,
            error_type=d.error_type,
            error_summary=d.error_summary,
            files_to_fix=[f.model_dump() for f in d.files_to_fix],
            commands_to_run=d.commands_to_run,
            confidence=d.confidence,
        )

    @classmethod
    def fallback(cls, reason: str) -> "DiagnosisResult":
        return cls(
            has_error=True,
            error_type="other",
            error_summary=f"Could not produce a diagnosis: {reason}",
            files_to_fix=[],
            commands_to_run=[],
            confidence="low",
        )


TESTING_SYSTEM_MESSAGE = """You are TITAN's QA Engineer and Error Detective — a senior developer who specializes in debugging.

## Your job
Given terminal output (stdout/stderr, a stack trace) and a project root, diagnose the ROOT
cause of any error and produce precise fix instructions matching the Diagnosis schema.

## Tools
- read_file: read the actual contents of a file the traceback points at, rather than guessing
  from the error text alone. Always read a file before claiming to know what's wrong with it.
- check_dependency: before recommending `pip install X` / `npm install X`, check whether X is
  already declared in requirements.txt / pyproject.toml / package.json. If it's already declared,
  the bug is probably not a missing dependency — look for a version mismatch, a typo in the
  import, or a virtualenv/install-step problem instead.

## Rules
1. Identify the ROOT cause, not the symptom. A traceback's last line is often a symptom of an
   earlier problem — read the file(s) involved before concluding.
2. Use check_dependency before ever setting fix_type to "install_package".
3. If the terminal output shows success with no errors or tracebacks, set has_error to false
   and leave files_to_fix/commands_to_run empty.
4. Be specific: name exact line numbers, variable names, and package names where the terminal
   output or file contents give you enough to do so.
5. Your final answer must match the Diagnosis schema exactly.
"""


def _safe_path(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"Path '{relative_path}' escapes the project root")
    return candidate


class TestingAgent:
    """
    Analyzes terminal output and produces actionable, verified fix instructions.

    Where the old version had to trust whatever "relevant files" the caller
    pre-selected and truncated, this agent has read_file and check_dependency
    tools so it decides for itself what to inspect before diagnosing — and
    won't recommend installing a package that's already declared.
    """

    def __init__(self, project_path: str = ".", provider: str | None = None):
        self.project_path = Path(project_path).resolve()
        self.provider = provider
        model = get_model_by_provider(provider) if provider else testing_model()
        tools = [
            FunctionTool(self.read_file),
            FunctionTool(self.check_dependency),
        ]
        self._agent = ChatAgent(
            system_message=TESTING_SYSTEM_MESSAGE,
            model=model,
            tools=tools,
        )
        logger.info(
            f"TestingAgent initialized (provider={provider or 'default groq'}, root={self.project_path})"
        )

    # ------------------------------------------------------------------
    # Tools exposed to the agent
    # ------------------------------------------------------------------

    def read_file(self, relative_path: str, max_chars: int = 6000) -> str:
        """Read a file inside the project the agent is debugging.

        Args:
            relative_path: Path relative to the project root.
            max_chars: Max characters to return (default 6000).

        Returns:
            The file's content, or an error string if it can't be read.
        """
        try:
            path = _safe_path(self.project_path, relative_path)
        except ValueError as exc:
            return f"ERROR: {exc}"
        if not path.exists() or not path.is_file():
            return f"ERROR: file does not exist: {relative_path}"
        try:
            return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
        except Exception as exc:
            return f"ERROR reading file: {exc}"

    def check_dependency(self, package_name: str) -> str:
        """Check whether a package is already declared in this project's manifests.

        Searches requirements.txt, pyproject.toml, and package.json (including
        devDependencies) for the given package name.

        Args:
            package_name: The package/import name to look for, e.g. "requests" or "axios".

        Returns:
            JSON string: {"declared": bool, "found_in": [manifest paths], "detail": str}
        """
        needle = package_name.strip().lower()
        found_in: list[str] = []

        req = self.project_path / "requirements.txt"
        if req.exists():
            try:
                for line in req.read_text(errors="ignore").splitlines():
                    line = line.strip().lower()
                    if line and not line.startswith("#") and line.split("==")[0].split(">=")[0].strip() == needle:
                        found_in.append("requirements.txt")
                        break
            except Exception:
                pass

        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            try:
                if needle in pyproject.read_text(errors="ignore").lower():
                    found_in.append("pyproject.toml")
            except Exception:
                pass

        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text(errors="ignore"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if any(k.lower() == needle for k in deps):
                    found_in.append("package.json")
            except Exception:
                pass

        return json.dumps(
            {
                "declared": bool(found_in),
                "found_in": found_in,
                "detail": (
                    f"'{package_name}' is already declared — likely not a missing-dependency issue."
                    if found_in
                    else f"'{package_name}' was not found in any manifest — may genuinely need installing."
                ),
            }
        )

    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------

    def diagnose(
        self,
        terminal_output: str,
        project_context: str = "",
        file_contents: dict[str, str] | None = None,
        **kwargs,
    ) -> DiagnosisResult:
        """
        Analyze terminal output and diagnose the root cause of any error.
        The agent reads real files and checks real manifests via its tools
        rather than relying on a pre-selected, pre-truncated context.
        """
        prompt = f"""
Project: {project_context or "(no description provided — infer from files as needed)"}
Project root: {self.project_path}

Terminal Output:
{terminal_output}

Diagnose this output. Read any files the traceback points at, and check_dependency before
recommending any install. Return a Diagnosis.
"""
        logger.info("TestingAgent diagnosing terminal output...")
        try:
            response = self._agent.step(prompt, response_format=Diagnosis)
            parsed: Diagnosis | None = getattr(response.msgs[0], "parsed", None)
            if parsed is None:
                parsed = Diagnosis.model_validate_json(response.msgs[0].content)
            result = DiagnosisResult.from_diagnosis(parsed)
        except Exception as exc:
            logger.error(f"TestingAgent failed to produce a diagnosis: {exc}")
            result = DiagnosisResult.fallback(str(exc))

        if result.has_error:
            logger.warning(f"Error detected: {result.error_type} — {result.error_summary}")
        else:
            logger.success("No errors detected — project running cleanly!")
        return result

    def reset(self):
        self._agent.reset()