"""
Project TITAN — Planner Agent
Uses Groq Llama 3.3 70B to decompose a user request (e.g. "Build a Netflix Clone")
into an ordered list of structured tasks that TITAN will execute.
"""

from __future__ import annotations

import json
import re
from typing import Any

from loguru import logger

from camel.agents import ChatAgent
from camel.types import ModelPlatformType
from backend.ai.model_factory import planner_model, get_model_by_provider


PLANNER_SYSTEM_MESSAGE = """You are TITAN's Master Planner — a world-class software architect and AI project manager.

Your job is to take a user's project request and break it down into a precise, ordered list of executable tasks.

## Rules
1. Return ONLY valid JSON — no markdown, no explanation outside the JSON.
2. Each task must be specific, actionable, and self-contained.
3. Order tasks from foundation to deployment (dependencies first).
4. Every task must have these exact fields: id, type, title, description, agent, file_path (if applicable), command (if applicable), content (if applicable).
5. Use these task types ONLY: create_folder, create_file, write_code, run_command, git_init, git_push, generate_readme, generate_gitignore, open_vscode.
6. Assign each task to one agent: planner, code, testing, docs, terminal, github, filesystem.
7. MAXIMUM 30 tasks total. Be concise. Combine related tasks.
8. ALWAYS complete the full JSON including ALL tasks before stopping.

## Output Format (strict JSON)
{
  "project_name": "string",
  "project_description": "string",
  "tech_stack": ["list", "of", "technologies"],
  "total_tasks": number,
  "tasks": [
    {
      "id": 1,
      "type": "create_folder",
      "title": "Create project root",
      "description": "Create the main project directory structure",
      "agent": "filesystem",
      "file_path": "project-name/",
      "command": null,
      "content": null
    }
  ]
}
"""


class PlannerAgent:

    """
    Breaks down a user project request into structured, executable tasks.
    Powered by Groq Llama 3.3 70B via CAMEL AI.
    """

    def __init__(self, provider: str = None):
        """Initialize the planner agent with an optional provider fallback."""
        model = get_model_by_provider(provider) if provider else planner_model()
        
        # We use a custom ChatAgent setup because the default JSON parser was
        # returning JSON when it received very large prompts.
        self._agent = ChatAgent(
            system_message=PLANNER_SYSTEM_MESSAGE,
            model=model,
        )
        logger.info(f"PlannerAgent initialized (Provider: {provider or 'default groq'})")

    def plan(self, user_request: str, extra_context: str = "") -> dict[str, Any]:
        """
        Takes a natural language project request and returns a structured plan.

        Args:
            user_request: e.g. "Build me a Spotify Clone using React and FastAPI"
            extra_context: Optional extra info (target OS, preferences, etc.)

        Returns:
            dict with keys: project_name, tech_stack, tasks, etc.
        """
        # Truncate very long prompts to avoid hitting context limits
        # Keep first 4000 chars which has enough info for the planner
        truncated = user_request[:4000]
        if len(user_request) > 4000:
            truncated += "\n\n[...prompt truncated for planning — full details will be passed to agents per-task...]"

        prompt = f"""
User Request: {truncated}

{f"Additional Context: {extra_context}" if extra_context else ""}

Generate a complete, ordered task plan as strict JSON.
Include ALL files needed: main files, config files, package.json/requirements.txt, .env.example, README, .gitignore.
Be thorough — a real developer would not miss any file.
Return ONLY the JSON object. No explanation, no markdown fences.
"""
        logger.info(f"Planning project: {user_request[:120]}...")

        # ── Planner-specific fallback: only use Groq (best JSON) ────────────
        # Mistral and Gemini sometimes return malformed JSON — Groq is the best
        # structured output model. We rotate across Groq models only if rate limited.
        groq_models = ["llama-3.3-70b-versatile", "llama3-8b-8192", "gemma2-9b-it"]
        from backend.ai.model_factory import get_groq_model, get_gemini_model
        fallback_models = [
            get_groq_model("llama-3.3-70b-versatile"),
            get_gemini_model("gemini-2.0-flash"),
            get_groq_model("llama3-8b-8192"),
        ]

        plan = {}
        for i, model in enumerate(fallback_models):
            try:
                self._agent._model_backend = model
                self._agent.reset()
                response = self._agent.step(prompt)
                raw = response.msgs[0].content.strip()
                plan = self._extract_json(raw)
                if plan.get("tasks"):  # Got a valid plan with tasks
                    break
                else:
                    logger.warning(f"Planner got empty tasks from model {i+1}, trying next...")
            except Exception as exc:
                err = str(exc).lower()
                if "429" in err or "rate_limit" in err or "quota" in err or "resource_exhausted" in err:
                    logger.warning(f"Planner rate limited on model {i+1}, trying next...")
                    continue
                else:
                    raise

        task_count = len(plan.get("tasks", []))
        logger.success(f"Plan created: {plan.get('project_name')} — {task_count} tasks")
        return plan


    def _extract_json(self, text: str) -> dict:
        """Robustly extract JSON from model response, including truncated responses."""
        # Step 1: Clean up code fences
        cleaned = text.strip()
        # Remove ```json / ``` wrappers
        match = re.search(r"```(?:json)?\s*([\s\S]+?)```", cleaned)
        if match:
            cleaned = match.group(1).strip()
        else:
            # Extract between first { and last }
            start = cleaned.find("{")
            if start != -1:
                cleaned = cleaned[start:]

        # Step 2: Try direct parse (fully valid JSON)
        try:
            result = json.loads(cleaned)
            if result.get("tasks"):
                return result
        except json.JSONDecodeError:
            pass

        # Step 3: Try to fix truncated JSON by closing open brackets
        try:
            fixed = self._repair_truncated_json(cleaned)
            result = json.loads(fixed)
            if result.get("tasks"):
                logger.warning(f"Used truncated-JSON repair — recovered {len(result['tasks'])} tasks")
                return result
        except Exception:
            pass

        # Step 4: Response was cut off BEFORE tasks array even started
        # Complete the partial JSON by appending the tasks field and closing
        try:
            # Find the partial object (has project_name but no tasks)
            partial = cleaned.rstrip().rstrip(",")
            # Ensure it ends at a proper boundary
            if partial.endswith('"') or partial[-1].isalnum() or partial[-1] in ']}':
                completed = partial + ', "tasks": [], "total_tasks": 0}'
                result = json.loads(completed)
                if result.get("project_name") and result["project_name"] != "unnamed-project":
                    logger.warning("JSON was truncated before tasks — will re-plan with next model")
                    # Return empty tasks so the caller retries with next model
                    return result
        except Exception:
            pass

        logger.error(f"Failed to parse planner JSON response. Raw (first 500 chars): {text[:500]}")
        return {
            "project_name": "unnamed-project",
            "project_description": "Generated project",
            "tech_stack": ["Python"],
            "total_tasks": 0,
            "tasks": [],
        }

    def _repair_truncated_json(self, text: str) -> str:
        """
        Attempt to repair a truncated JSON string by:
        1. Finding the last complete task object.
        2. Closing all open arrays/objects.
        """
        # Find last complete task object (ends with })
        # Walk backwards to find last complete closing brace for a task
        last_valid_task_end = -1
        depth = 0
        in_string = False
        escape_next = False

        for i, ch in enumerate(text):
            if escape_next:
                escape_next = False
                continue
            if ch == "\\" and in_string:
                escape_next = True
                continue
            if ch == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 1:  # Closed a task-level object, still inside tasks array
                    last_valid_task_end = i

        if last_valid_task_end == -1:
            return text  # Can't repair

        # Truncate to last valid task and close the structure
        truncated = text[: last_valid_task_end + 1]
        # Ensure the outer structure is closed
        # Count unclosed brackets in what we have
        open_brackets = truncated.count("[") - truncated.count("]")
        open_braces = truncated.count("{") - truncated.count("}")

        closing = ""
        # Close tasks array
        if open_brackets > 0:
            closing += "]" * open_brackets
        # Close root object
        if open_braces > 0:
            closing += "}" * open_braces

        repaired = truncated + closing
        return repaired

    def reset(self):
        self._agent.reset()

