"""
Project TITAN — Testing Agent
Uses Groq Llama 3.3 70B to analyze terminal errors, diagnose root causes,
and suggest precise code fixes. Iterates until the project runs cleanly.
"""

from __future__ import annotations

from dataclasses import dataclass
from loguru import logger

from camel.agents import ChatAgent
from camel.types import ModelPlatformType
import os
from backend.ai.model_factory import testing_model, get_model_by_provider


TESTING_SYSTEM_MESSAGE = """You are TITAN's QA Engineer and Error Detective — a senior developer who specializes in debugging.

## Your Job
Analyze terminal output (errors, warnings, stack traces) and return precise fix instructions.

## Rules
1. Read the error carefully — identify the ROOT cause, not symptoms.
2. Return a JSON response with this exact structure:
{
  "has_error": true/false,
  "error_type": "import_error | syntax_error | runtime_error | missing_dep | config_error | other",
  "error_summary": "brief description",
  "files_to_fix": [
    {
      "file_path": "path/to/file.py",
      "fix_description": "What to change and why",
      "fix_type": "edit_code | install_package | create_file | run_command"
    }
  ],
  "commands_to_run": ["pip install missing-package"],
  "confidence": "high | medium | low"
}
3. If the output shows SUCCESS (no errors), set has_error to false.
4. Be specific — name the exact line numbers, variable names, and packages involved.
"""


@dataclass
class DiagnosisResult:
    has_error: bool
    error_type: str
    error_summary: str
    files_to_fix: list[dict]
    commands_to_run: list[str]
    confidence: str


class TestingAgent:
    """
    Analyzes errors from terminal output and produces actionable fix instructions.
    Powered by Groq Llama 3.3 70B via CAMEL AI.
    """

    def __init__(self, provider: str = None):
        model = get_model_by_provider(provider) if provider else testing_model()
        self._agent = ChatAgent(
            system_message=TESTING_SYSTEM_MESSAGE,
            model=model,
        )
        logger.info(f"TestingAgent initialized (Provider: {provider or 'default groq'})")

    def diagnose(
        self,
        terminal_output: str,
        project_context: str = "",
        file_contents: dict[str, str] | None = None,
    ) -> DiagnosisResult:
        """
        Analyze terminal output and diagnose errors.

        Args:
            terminal_output: stdout + stderr from running the project
            project_context: Brief project description
            file_contents: Dict of {filepath: content} for relevant files

        Returns:
            DiagnosisResult with fix instructions
        """
        import json, re

        file_section = ""
        if file_contents:
            file_section = "\n\nRelevant File Contents:\n"
            for path, content in list(file_contents.items())[:3]:
                preview = content[:800] + "..." if len(content) > 800 else content
                file_section += f"\n--- {path} ---\n{preview}\n"

        prompt = f"""
Project: {project_context}

Terminal Output:
{terminal_output}
{file_section}

Analyze this output. Return diagnosis as strict JSON only.
"""
        logger.info("TestingAgent diagnosing terminal output...")
        response = self._agent.step(prompt)
        raw = response.msgs[0].content.strip()

        # Parse JSON
        result = self._parse_diagnosis(raw)
        if result.has_error:
            logger.warning(f"Error detected: {result.error_type} — {result.error_summary}")
        else:
            logger.success("No errors detected — project running cleanly!")
        return result

    def _parse_diagnosis(self, text: str) -> DiagnosisResult:
        import json, re

        # Extract JSON
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]+\}", text)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    data = {}
            else:
                data = {}

        return DiagnosisResult(
            has_error=data.get("has_error", False),
            error_type=data.get("error_type", "unknown"),
            error_summary=data.get("error_summary", "Unknown error"),
            files_to_fix=data.get("files_to_fix", []),
            commands_to_run=data.get("commands_to_run", []),
            confidence=data.get("confidence", "low"),
        )

    def reset(self):
        self._agent.reset()
