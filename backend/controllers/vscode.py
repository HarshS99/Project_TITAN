"""
Project TITAN — VS Code Controller
Opens VS Code in project directories and specific files.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from loguru import logger


class VSCodeController:
    """Opens VS Code in the project directory."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def open_project(self) -> bool:
        """Open the project in VS Code."""
        try:
            result = subprocess.run(
                f"code '{self.project_root}'",
                shell=True,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                logger.success(f"✅ Opened VS Code: {self.project_root}")
                return True
            else:
                logger.warning(f"code CLI not found, trying 'open' (macOS): {result.stderr}")
                subprocess.run(f"open -a 'Visual Studio Code' '{self.project_root}'",
                               shell=True)
                return True
        except Exception as e:
            logger.error(f"open_project failed: {e}")
            return False

    def open_file(self, relative_path: str, line: int | None = None) -> bool:
        """Open a specific file in VS Code, optionally at a line number."""
        file_path = self.project_root / relative_path
        cmd = f"code '{file_path}'"
        if line:
            cmd = f"code -g '{file_path}:{line}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0

    def is_available(self) -> bool:
        """Check if VS Code CLI is available."""
        result = subprocess.run("code --version", shell=True,
                                capture_output=True, text=True)
        return result.returncode == 0
