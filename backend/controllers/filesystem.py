"""
Project TITAN — File System Controller
Handles all file and folder operations for generated projects.
Uses pathlib for safe, cross-platform file operations.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from loguru import logger

from backend.config import PROJECTS_DIR


class FilesystemController:
    """
    Manages file and folder operations within the TITAN projects directory.
    All paths are sandboxed inside PROJECTS_DIR for safety.
    """

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_root = PROJECTS_DIR / project_name
        self.project_root.mkdir(parents=True, exist_ok=True)
        logger.info(f"FilesystemController ready: {self.project_root}")

    def resolve(self, relative_path: str) -> Path:
        """Safely resolve a path relative to the project root."""
        full = (self.project_root / relative_path).resolve()
        # Safety: ensure path stays inside project root
        if not str(full).startswith(str(self.project_root.resolve())):
            raise ValueError(f"Path escape attempt blocked: {relative_path}")
        return full

    # ── Folder Operations ─────────────────────────────────────

    def create_folder(self, relative_path: str) -> Path:
        """Create a folder (and all parents) relative to project root."""
        path = self.resolve(relative_path)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Created folder: {relative_path}")
        return path

    def delete_folder(self, relative_path: str, confirm: bool = True) -> bool:
        """Delete a folder and all its contents."""
        if confirm:
            logger.warning(f"Deleting folder: {relative_path}")
        path = self.resolve(relative_path)
        if path.exists():
            shutil.rmtree(path)
            logger.info(f"🗑️  Deleted folder: {relative_path}")
            return True
        return False

    # ── File Operations ───────────────────────────────────────

    def create_file(self, relative_path: str, content: str = "") -> Path:
        """Create a file with optional initial content."""
        path = self.resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.info(f"📄 Created file: {relative_path} ({len(content)} chars)")
        return path

    def write_file(self, relative_path: str, content: str) -> Path:
        """Write (overwrite) a file with content."""
        return self.create_file(relative_path, content)

    def read_file(self, relative_path: str) -> str:
        """Read and return file content."""
        path = self.resolve(relative_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        return path.read_text(encoding="utf-8")

    def append_file(self, relative_path: str, content: str) -> Path:
        """Append content to an existing file."""
        path = self.resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        return path

    def delete_file(self, relative_path: str) -> bool:
        """Delete a file."""
        path = self.resolve(relative_path)
        if path.exists():
            path.unlink()
            logger.info(f"🗑️  Deleted file: {relative_path}")
            return True
        return False

    def file_exists(self, relative_path: str) -> bool:
        """Check if a file exists."""
        return self.resolve(relative_path).exists()

    def rename_file(self, old_path: str, new_path: str) -> Path:
        """Rename/move a file within the project."""
        src = self.resolve(old_path)
        dst = self.resolve(new_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)
        logger.info(f"✏️  Renamed: {old_path} → {new_path}")
        return dst

    # ── Tree / Search ─────────────────────────────────────────

    def get_file_tree(self, max_depth: int = 5) -> dict:
        """Return the project file tree as a nested dict."""
        def _build_tree(path: Path, depth: int = 0) -> dict:
            if depth >= max_depth:
                return {}
            result = {}
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith(".") and item.name not in {".env.example", ".gitignore"}:
                        continue
                    if item.name in {"node_modules", "__pycache__", ".git", "venv", ".venv"}:
                        continue
                    if item.is_dir():
                        result[item.name + "/"] = _build_tree(item, depth + 1)
                    else:
                        result[item.name] = item.stat().st_size
            except PermissionError:
                pass
            return result
        return _build_tree(self.project_root)

    def get_all_files(self, extensions: list[str] | None = None) -> list[str]:
        """Return all file paths relative to project root, optionally filtered by extension."""
        files = []
        for p in self.project_root.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(self.project_root))
                # Skip hidden dirs and common ignored dirs
                if any(part.startswith(".") or part in {"node_modules", "__pycache__", "venv", ".venv"}
                       for part in p.parts):
                    continue
                if extensions is None or p.suffix in extensions:
                    files.append(rel)
        return sorted(files)

    def get_project_contents(self, max_files: int = 20) -> dict[str, str]:
        """Return dict of {filepath: content} for all project files (limited)."""
        files = self.get_all_files()[:max_files]
        contents = {}
        for f in files:
            try:
                contents[f] = self.read_file(f)
            except Exception:
                pass
        return contents

    @property
    def root(self) -> Path:
        return self.project_root
