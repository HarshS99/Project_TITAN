"""
Project TITAN — Session Memory
SQLite-based persistent memory for tracking project builds,
task history, agent decisions, and error logs.
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select
from loguru import logger

from backend.config import DB_PATH


# ── Models ─────────────────────────────────────────────────────────────────

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProjectRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    tech_stack: str  # JSON list
    status: str = "building"  # building | done | failed
    github_url: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    total_tasks: int = 0
    completed_tasks: int = 0


class TaskRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int
    task_id: int
    task_type: str
    title: str
    description: str
    agent: str
    file_path: str = ""
    status: str = TaskStatus.PENDING
    result: str = ""  # JSON or text
    error: str = ""
    started_at: str = ""
    completed_at: str = ""


class AgentLogRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int
    agent: str
    action: str
    message: str
    level: str = "info"  # info | success | warning | error
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ── Database Setup ─────────────────────────────────────────────────────────

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
        SQLModel.metadata.create_all(_engine)
        logger.info(f"Database ready: {DB_PATH}")
    return _engine


# ── SessionMemory Class ────────────────────────────────────────────────────

class SessionMemory:
    """
    Persistent session memory for TITAN.
    Tracks projects, tasks, and agent activity across runs.
    """

    def __init__(self):
        self._engine = get_engine()

    # ── Projects ─────────────────────────────────────────────

    def create_project(
        self,
        name: str,
        description: str,
        tech_stack: list[str],
        total_tasks: int = 0,
    ) -> int:
        """Create a new project record. Returns project ID."""
        with Session(self._engine) as session:
            project = ProjectRecord(
                name=name,
                description=description,
                tech_stack=json.dumps(tech_stack),
                total_tasks=total_tasks,
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            logger.info(f"Project created in DB: {name} (ID: {project.id})")
            return project.id

    def update_project_status(self, project_id: int, status: str, github_url: str = "") -> None:
        with Session(self._engine) as session:
            project = session.get(ProjectRecord, project_id)
            if project:
                project.status = status
                project.updated_at = datetime.now().isoformat()
                if github_url:
                    project.github_url = github_url
                session.add(project)
                session.commit()

    def increment_completed_tasks(self, project_id: int) -> None:
        with Session(self._engine) as session:
            project = session.get(ProjectRecord, project_id)
            if project:
                project.completed_tasks += 1
                project.updated_at = datetime.now().isoformat()
                session.add(project)
                session.commit()

    def get_project(self, project_id: int) -> Optional[ProjectRecord]:
        with Session(self._engine) as session:
            return session.get(ProjectRecord, project_id)

    def list_projects(self) -> list[ProjectRecord]:
        with Session(self._engine) as session:
            return session.exec(select(ProjectRecord).order_by(ProjectRecord.id.desc())).all()

    # ── Tasks ─────────────────────────────────────────────────

    def save_task(self, project_id: int, task: dict) -> int:
        """Save a task to the database. Returns task record ID."""
        with Session(self._engine) as session:
            record = TaskRecord(
                project_id=project_id,
                task_id=task.get("id", 0),
                task_type=task.get("type", ""),
                title=task.get("title", ""),
                description=task.get("description", ""),
                agent=task.get("agent", ""),
                file_path=task.get("file_path", "") or "",
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record.id

    def update_task_status(
        self,
        record_id: int,
        status: TaskStatus,
        result: str = "",
        error: str = "",
    ) -> None:
        with Session(self._engine) as session:
            task = session.get(TaskRecord, record_id)
            if task:
                task.status = status
                task.result = result
                task.error = error
                if status == TaskStatus.IN_PROGRESS:
                    task.started_at = datetime.now().isoformat()
                elif status in (TaskStatus.DONE, TaskStatus.FAILED):
                    task.completed_at = datetime.now().isoformat()
                session.add(task)
                session.commit()

    def get_project_tasks(self, project_id: int) -> list[TaskRecord]:
        with Session(self._engine) as session:
            return session.exec(
                select(TaskRecord).where(TaskRecord.project_id == project_id)
            ).all()

    # ── Agent Logs ────────────────────────────────────────────

    def log(self, project_id: int, agent: str, action: str, message: str, level: str = "info") -> None:
        with Session(self._engine) as session:
            record = AgentLogRecord(
                project_id=project_id,
                agent=agent,
                action=action,
                message=message,
                level=level,
            )
            session.add(record)
            session.commit()

    def get_logs(self, project_id: int, limit: int = 100) -> list[AgentLogRecord]:
        with Session(self._engine) as session:
            return session.exec(
                select(AgentLogRecord)
                .where(AgentLogRecord.project_id == project_id)
                .order_by(AgentLogRecord.id.desc())
                .limit(limit)
            ).all()
