"""
Project TITAN — Code Agent
Uses Gemini 3.8 Flash (with Groq fallback) to write production-quality code for any file.
Receives task context (file path, description, tech stack) and outputs
clean, complete, well-commented code.
"""

from __future__ import annotations

from camel.agents import ChatAgent
from loguru import logger

from backend.ai.model_factory import (
    code_model,
    get_gemini_model,
    get_groq_model,
    get_model_by_provider,
)

CODE_SYSTEM_MESSAGE = """You are TITAN's Senior Software Engineer — an elite developer who writes production-quality code.

## Your Rules
1. Write COMPLETE files — never truncate or use placeholders like "# ... rest of code".
2. Include proper imports, error handling, type hints, and docstrings.
3. Follow best practices for the given language/framework.
4. Add inline comments for complex logic.
5. Make code that actually RUNS without modification.
6. Never include markdown code fences (```) in your output — return raw code only.
7. If writing Python: use type hints, f-strings, pathlib for paths.
8. If writing JavaScript/TypeScript: use modern ES6+, async/await.
9. If writing HTML/CSS: write clean, semantic, responsive code.
10. CRITICAL — If the file extension is .js, NEVER use TypeScript syntax. This means:
    - NO type annotations (e.g. `req: Request` is FORBIDDEN in .js files)
    - NO TypeScript imports like `import { Request, Response } from 'express'`
    - NO interface or type declarations
    - Use plain JavaScript: `app.get('/route', async (req, res) => { ... })`
    - TypeScript syntax is ONLY allowed in .ts files.

## Output
Return ONLY the file content. No explanation. No markdown. Just the raw code.
"""

# Fallback ladder: tried in order when the primary model fails.
# Each entry is (provider, model_name).
FALLBACK_MODELS = [
    ("gemini", "gemini-2.5-flash"),
    ("groq",   "openai/gpt-oss-120b"),
    ("groq",   "qwen/qwen3.8-27b"),
]


def _strip_fences(code: str) -> str:
    """Remove accidental markdown code fences from a response."""
    if code.startswith("```"):
        lines = code.split("\n")
        code = (
            "\n".join(lines[1:-1])
            if lines[-1].strip() == "```"
            else "\n".join(lines[1:])
        )
    return code


def _make_agent(provider: str, model_name: str) -> ChatAgent:
    """Build a ChatAgent for the given provider/model."""
    if provider == "gemini":
        model = get_gemini_model(model_name)
    else:
        model = get_groq_model(model_name)
    return ChatAgent(system_message=CODE_SYSTEM_MESSAGE, model=model)


class CodeAgent:
    """
    Writes complete, production-ready code files.
    Powered by Gemini 3.8 Flash (with Groq fallback) via CAMEL AI.
    """

    def __init__(self, provider: str | None = None):
        self._provider = provider
        self._agent = ChatAgent(
            system_message=CODE_SYSTEM_MESSAGE,
            model=get_model_by_provider(provider) if provider else code_model(),
        )
        logger.info(f"CodeAgent initialized (Provider: {provider or 'default gemini'})")

    # ------------------------------------------------------------------
    # Internal: run prompt with automatic model fallback
    # ------------------------------------------------------------------
    def _step_with_fallback(self, prompt: str) -> str:
        """
        Try the primary agent first, then walk through FALLBACK_MODELS on error.
        Always resets the agent before each attempt to avoid token accumulation.
        """
        self._agent.reset()
        try:
            response = self._agent.step(prompt)
            if not response.msgs:
                return ""
            return response.msgs[0].content.strip()
        except Exception as primary_err:
            logger.warning(f"CodeAgent primary model failed: {primary_err}")

        for provider, model_name in FALLBACK_MODELS:
            try:
                logger.info(f"CodeAgent trying fallback: {provider}:{model_name}")
                fallback_agent = _make_agent(provider, model_name)
                response = fallback_agent.step(prompt)
                if not response.msgs:
                    return ""
                return response.msgs[0].content.strip()
            except Exception as err:
                logger.warning(f"CodeAgent fallback {provider}:{model_name} failed: {err}")

        raise RuntimeError(
            "CodeAgent: all models (primary + fallbacks) failed to produce code."
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def write_code(
        self,
        file_path: str,
        description: str,
        tech_stack: list[str],
        project_context: str = "",
        existing_files: dict[str, str] | None = None,
    ) -> str:
        """
        Generate code for a specific file.

        Args:
            file_path: Target file path (e.g. 'backend/main.py')
            description: What this file should do
            tech_stack: List of technologies being used
            project_context: High-level project description
            existing_files: Dict of {filename: content} for already-created files (for context)

        Returns:
            Raw file content as string
        """
        context_section = ""
        if existing_files:
            # Hard-limit: only send the 2 most recent files with tiny previews
            # to avoid 413 token limit errors on Groq's free tier
            shown = list(existing_files.items())[-2:]
            context_section = "\n\nRecent files (short preview):\n"
            for fname, content in shown:
                preview = content[:200] + "..." if len(content) > 200 else content
                context_section += f"\n--- {fname} ---\n{preview}\n"

        prompt = f"""
Project: {project_context[:300]}
Tech Stack: {", ".join(tech_stack[:8])}
File to write: {file_path}
Description: {description[:600]}
{context_section}

Write the complete content for: {file_path}
Return ONLY the raw file content, nothing else.
"""
        logger.info(f"CodeAgent writing: {file_path}")
        code = _strip_fences(self._step_with_fallback(prompt))
        logger.success(f"CodeAgent wrote {len(code)} chars → {file_path}")
        return code

    def fix_code(
        self,
        file_path: str,
        current_code: str,
        error_message: str,
        context: str = "",
    ) -> str:
        """
        Fix broken code based on an error message.

        Args:
            file_path: The file that has the error
            current_code: The current (broken) code
            error_message: The error/exception from terminal
            context: Additional context

        Returns:
            Fixed file content
        """
        prompt = f"""
File: {file_path}
Error:
{error_message}

Current Code:
{current_code}

{f"Context: {context}" if context else ""}

Fix the code. Return ONLY the complete fixed file content.
"""
        logger.info(f"CodeAgent fixing error in: {file_path}")
        fixed = _strip_fences(self._step_with_fallback(prompt))
        logger.success(f"CodeAgent fixed {len(fixed)} chars → {file_path}")
        return fixed

    def reset(self):
        """Reset agent memory."""
        self._agent.reset()
