"""
Project TITAN — Terminal Controller
Executes shell commands in the project directory, captures output,
and streams results for the UI. Handles installs, running servers, git, etc.
"""

from __future__ import annotations

import subprocess
import shlex
import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import Generator

from loguru import logger


@dataclass
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    success: bool

    @property
    def output(self) -> str:
        """Combined stdout + stderr."""
        parts = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(self.stderr)
        return "\n".join(parts)


class TerminalController:
    """
    Runs shell commands in a project's directory.
    Provides sync and async execution with timeout support.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        logger.info(f"TerminalController ready at: {project_root}")

    def run(
        self,
        command: str,
        timeout: int = 120,
        env: dict | None = None,
    ) -> CommandResult:
        """
        Run a shell command synchronously.

        Args:
            command: Shell command string
            timeout: Max seconds to wait (default 120)
            env: Optional extra environment variables

        Returns:
            CommandResult with stdout, stderr, returncode
        """
        import os
        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        logger.info(f"🖥️  Running: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=full_env,
            )
            cmd_result = CommandResult(
                command=command,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                success=result.returncode == 0,
            )
            if cmd_result.success:
                logger.success(f"✅ Command succeeded: {command}")
            else:
                logger.warning(f"❌ Command failed (rc={result.returncode}): {command}")
                if result.stderr:
                    logger.debug(f"STDERR: {result.stderr[:500]}")
            return cmd_result

        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Command timed out after {timeout}s: {command}")
            return CommandResult(
                command=command,
                returncode=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                success=False,
            )
        except Exception as e:
            logger.error(f"Command error: {e}")
            return CommandResult(
                command=command,
                returncode=-1,
                stdout="",
                stderr=str(e),
                success=False,
            )

    def run_stream(self, command: str, timeout: int = 300) -> Generator[str, None, None]:
        """
        Run a command and yield output lines as they arrive (for live streaming to UI).

        Yields:
            Lines of stdout/stderr output
        """
        import os
        logger.info(f"🖥️  Streaming: {command}")
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=os.environ.copy(),
        )
        try:
            for line in iter(process.stdout.readline, ""):
                yield line.rstrip()
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            yield f"[TITAN] Command timed out after {timeout}s"
        finally:
            if process.stdout:
                process.stdout.close()

    def install_python_deps(self, requirements_file: str = "requirements.txt") -> CommandResult:
        """Install Python dependencies."""
        return self.run(f"pip install -r {requirements_file}", timeout=180)

    def install_node_deps(self) -> CommandResult:
        """Install Node.js dependencies."""
        return self.run("npm install", timeout=180)

    def run_python(self, script: str) -> CommandResult:
        """Run a Python script."""
        return self.run(f"python {script}", timeout=60)

    def run_node(self, script: str = "index.js") -> CommandResult:
        """Run a Node.js script."""
        return self.run(f"node {script}", timeout=60)

    def open_vscode(self) -> CommandResult:
        """Open VS Code in the project directory."""
        return self.run(f"code {self.project_root}", timeout=10)

    def get_python_version(self) -> str:
        result = self.run("python --version", timeout=10)
        return result.stdout.strip() or result.stderr.strip()

    def get_node_version(self) -> str:
        result = self.run("node --version", timeout=10)
        return result.stdout.strip()
