"""
Project TITAN — Docs Agent
Uses Groq Llama 3.3 70B to generate professional documentation:
README.md, .gitignore, LICENSE, CONTRIBUTING.md, GitHub Actions CI/CD.
"""

from __future__ import annotations

from loguru import logger

from camel.agents import ChatAgent
from camel.types import ModelPlatformType
import os
from backend.ai.model_factory import docs_model, get_model_by_provider


DOCS_SYSTEM_MESSAGE = """You are TITAN's Documentation Engineer — you write stunning, professional project documentation.

## Rules
1. Return ONLY the raw file content — no markdown fences, no explanation.
2. For README: use badges, emojis, proper sections, architecture diagrams (ASCII), setup instructions.
3. For .gitignore: be thorough for the given tech stack.
4. For GitHub Actions: write working, production-ready YAML.
5. Make it look like a professional open-source project, not a student assignment.
"""


class DocsAgent:
    """
    Generates professional project documentation.
    Powered by Groq Llama 3.3 70B via CAMEL AI.
    """

    def __init__(self, provider: str = None):
        model = get_model_by_provider(provider) if provider else docs_model()
        self._agent = ChatAgent(
            system_message=DOCS_SYSTEM_MESSAGE,
            model=model,
        )
        logger.info(f"DocsAgent initialized (Provider: {provider or 'default mistral'})")

    def generate_readme(
        self,
        project_name: str,
        description: str,
        tech_stack: list[str],
        features: list[str],
        github_username: str = "",
        repo_name: str = "",
    ) -> str:
        """Generate a professional README.md."""
        prompt = f"""
Project Name: {project_name}
Description: {description}
Tech Stack: {", ".join(tech_stack)}
Key Features: {", ".join(features)}
GitHub: {"github.com/" + github_username + "/" + repo_name if github_username else ""}

Write a professional, stunning README.md with:
- Title and badges (build, license, Python/Node version, GitHub stars)
- Short description with emoji
- Features list with checkmarks
- Tech Stack section with badges/icons
- Getting Started (Prerequisites + Installation steps)
- Usage examples
- Folder Structure (tree view)
- API Documentation (if applicable)
- Contributing section
- License (MIT)
- ASCII art architecture diagram

Return ONLY the README.md content.
"""
        logger.info(f"DocsAgent generating README for: {project_name}")
        response = self._agent.step(prompt)
        return response.msgs[0].content.strip()

    def generate_gitignore(self, tech_stack: list[str]) -> str:
        """Generate a comprehensive .gitignore."""
        prompt = f"""
Tech Stack: {", ".join(tech_stack)}

Generate a comprehensive .gitignore file for this tech stack.
Include: OS files, editor files, dependency directories, build outputs, env files, logs, secrets.
Return ONLY the .gitignore content.
"""
        response = self._agent.step(prompt)
        return response.msgs[0].content.strip()

    def generate_license(self, author_name: str = "Project TITAN") -> str:
        """Generate MIT LICENSE."""
        from datetime import datetime
        year = datetime.now().year
        return f"""MIT License

Copyright (c) {year} {author_name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

    def generate_github_actions(self, tech_stack: list[str], project_type: str = "python") -> str:
        """Generate GitHub Actions CI/CD workflow."""
        prompt = f"""
Tech Stack: {", ".join(tech_stack)}
Project Type: {project_type}

Generate a production-ready GitHub Actions CI/CD workflow file (.github/workflows/ci.yml).
Include: dependency install, linting, testing, build steps.
Return ONLY the YAML content.
"""
        response = self._agent.step(prompt)
        content = response.msgs[0].content.strip()
        # Remove markdown fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        return content

    def generate_contributing(self, project_name: str) -> str:
        """Generate CONTRIBUTING.md."""
        prompt = f"""
Project: {project_name}
Write a professional CONTRIBUTING.md with: how to fork, branch naming, PR process, code standards.
Return ONLY the file content.
"""
        response = self._agent.step(prompt)
        return response.msgs[0].content.strip()

    def reset(self):
        self._agent.reset()