"""
Project TITAN — Docs Agent
A real CAMEL agent: given only a project path, it explores the codebase
itself via tools, decides what documentation is needed, generates it, and
writes it to disk — no pre-computed inputs, no scripted single-shot prompts.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from camel.agents import ChatAgent
from camel.toolkits import FileToolkit, FunctionTool
from loguru import logger

from backend.ai.model_factory import docs_model, get_model_by_provider

AGENT_SYSTEM_MESSAGE = """You are TITAN's Documentation Engineer, an autonomous agent \
responsible for producing professional documentation for a software project.

You have tools to explore the project (list_directory, read_file, get_git_remote_info) \
and tools to write files (write_file). You are NOT \
given the project's name, tech stack, or description up front — you must discover all \
of it yourself using your tools.

Given a project root, your job is to:
1. Call list_directory to see the project's structure.
2. Call read_file on the files that matter most (package.json, requirements.txt,
   pyproject.toml, Cargo.toml, go.mod, main entry points, any existing README) to
   understand the tech stack, purpose, and features.
3. Call get_git_remote_info to find the GitHub username/repo name, if any.
4. Decide, based on what you actually found, what documentation this project needs.
   At minimum produce:
   - README.md — badges, emoji, features with checkmarks, tech stack, getting started,
     usage, folder structure (tree view), ASCII architecture diagram, contributing
     section, license section.
   - .gitignore — thorough, specific to the detected tech stack.
   - LICENSE — MIT, correct current year and author/org name.
   - CONTRIBUTING.md — fork/branch/PR process, code standards.
   - .github/workflows/ci.yml — a working GitHub Actions workflow (install, lint, test, build).
   - .vscode/tasks.json — install + run tasks, both with "runOptions": {"runOn": "folderOpen"},
     with the run task depending on the install task.
5. Actually write every file with your file-writing tool — do not just describe them.
6. Finish with a short plain-text summary of what you explored and what you wrote.

Rules:
- Base every file on what you actually found in the project. Don't invent tech stack
  or features that aren't evidenced by the files you read.
- If a doc file already exists, read it first and improve on it rather than ignoring it.
- Write final, real content — no "TODO" placeholders unless information is genuinely
  unavailable even after exploring.
- Do not wrap file content in markdown fences when writing to disk.
"""


def _safe_path(root: Path, relative_path: str) -> Path:
    """Resolve relative_path under root, refusing to let it escape the project."""
    candidate = (root / relative_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"Path '{relative_path}' escapes the project root")
    return candidate


class DocsAgent:
    """
    An autonomous CAMEL agent for project documentation.

    Unlike a set of single-shot prompt wrappers, this agent is handed tools
    (list_directory, read_file, get_git_remote_info, write_to_file) and a
    goal. CAMEL's ChatAgent.step() runs the full tool-calling loop internally:
    the model decides which tools to call, in what order, how many times, and
    when it has enough information to write the final files and stop.
    """

    SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".next"}

    def __init__(self, project_path: str = ".", provider: str | None = None):
        self.project_path = Path(project_path).resolve()
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {self.project_path}")

        model = get_model_by_provider(provider) if provider else docs_model()

        tools = [
            FunctionTool(self.list_directory),
            FunctionTool(self.read_file),
            FunctionTool(self.get_git_remote_info),
            FunctionTool(self.write_file),
        ]

        self._agent = ChatAgent(
            system_message=AGENT_SYSTEM_MESSAGE,
            model=model,
            tools=tools,
        )
        logger.info(
            f"DocsAgent initialized as autonomous CAMEL agent "
            f"(provider={provider or 'default'}, root={self.project_path})"
        )

    # ------------------------------------------------------------------
    # Tools exposed to the agent. Docstrings double as the tool schema
    # CAMEL sends to the model, so they're written for the model to read.
    # ------------------------------------------------------------------

    def list_directory(self, relative_path: str = ".", max_depth: int = 2) -> str:
        """List files under a path inside the project, up to a depth limit.

        Args:
            relative_path: Path relative to the project root ("." for root).
            max_depth: How many directory levels deep to descend (default 2).

        Returns:
            A newline-separated list of relative file paths, or an error string.
        """
        root = _safe_path(self.project_path, relative_path)
        if not root.exists():
            return f"ERROR: path does not exist: {relative_path}"

        base_depth = len(root.parts)
        found = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in self.SKIP_DIRS]
            depth = len(Path(dirpath).parts) - base_depth
            if depth >= max_depth:
                dirnames[:] = []
            rel_dir = Path(dirpath).relative_to(self.project_path)
            for fname in filenames:
                found.append(str(rel_dir / fname))
        return "\n".join(sorted(found)) or "(empty)"

    def read_file(self, relative_path: str, max_chars: int = 4000) -> str:
        """Read a text file inside the project.

        Args:
            relative_path: Path relative to the project root.
            max_chars: Max characters to return (default 4000, to bound context use).

        Returns:
            The file's content (truncated to max_chars), or an error string.
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

    def get_git_remote_info(self, dummy: str = "") -> str:
        """Get GitHub username/repo and inferred project name from git config.

        Returns:
            JSON string: {"github_username": str, "repo_name": str, "project_name": str}.
        """
        info = {
            "github_username": "",
            "repo_name": "",
            "project_name": self.project_path.name,
        }
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            url = result.stdout.strip()
            if url:
                cleaned = url.rstrip("/")
                if cleaned.endswith(".git"):
                    cleaned = cleaned[: -len(".git")]
                info["repo_name"] = cleaned.split("/")[-1]
                if "github.com" in cleaned:
                    tail = cleaned.split("github.com")[-1].lstrip(":/")
                    parts = tail.split("/")
                    if len(parts) >= 2:
                        info["github_username"], info["repo_name"] = parts[0], parts[1]
                info["project_name"] = info["repo_name"] or info["project_name"]
        except Exception as exc:
            info["error"] = str(exc)
        return json.dumps(info)

    def write_file(self, relative_path: str, content: str) -> str:
        """Write content to a file inside the project.

        Args:
            relative_path: Path relative to the project root.
            content: The text content to write.

        Returns:
            A success message or error string.
        """
        try:
            path = _safe_path(self.project_path, relative_path)
        except ValueError as exc:
            return f"ERROR: {exc}"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"SUCCESS: Wrote to {relative_path}"
        except Exception as exc:
            return f"ERROR writing file: {exc}"

    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------

    def run(self, instructions: str = "") -> str:
        """
        Let the agent autonomously explore the project and generate + write
        all documentation. Returns the agent's final summary text.
        """
        task = (
            f"The project root is '{self.project_path}'. Explore it, figure out what "
            f"it actually is, and generate and write all required documentation files."
        )
        if instructions:
            task += f"\n\nAdditional instructions: {instructions}"

        logger.info(f"DocsAgent run starting on {self.project_path}")
        response = self._agent.step(task)

        for call in response.info.get("tool_calls", []):
            logger.info(f"Tool call: {getattr(call, 'tool_name', call)}")

        summary = response.msgs[0].content.strip() if response.msgs else ""
        logger.info("DocsAgent run complete")
        return summary

    def reset(self):
        self._agent.reset()


if __name__ == "__main__":
    agent = DocsAgent(project_path=".")
    print(agent.run())