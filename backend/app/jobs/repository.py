from __future__ import annotations

import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

from app.core.errors import RuneError
from app.jobs.enums import (
    ACTIVE_JOB_STATUSES,
    ALLOWED_JOB_TRANSITIONS,
    JobStatus,
    SourceType,
)
from app.jobs.types import Job
from app.storage.database import connect_database


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class JobRepository:
    def __init__(self, database_path: Path) -> None:
        self._connection = connect_database(database_path)
        self._lock = threading.RLock()
        self._create_schema()

    def _create_schema(self) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    source_type TEXT NOT NULL,
                    source_label TEXT NOT NULL,
                    source_url TEXT,
                    source_path TEXT,
                    status TEXT NOT NULL,
                    progress INTEGER NOT NULL DEFAULT 0,
                    message TEXT NOT NULL,
                    error_code TEXT,
                    error_message TEXT,
                    media_title TEXT,
                    media_duration REAL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT
                )
                """
            )

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def create_job(
        self,
        *,
        source_type: SourceType,
        source_label: str,
        source_url: str | None = None,
        source_path: str | None = None,
    ) -> Job:
        now = _utc_now()
        job_id = uuid.uuid4().hex
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO jobs (
                    id, source_type, source_label, source_url, source_path,
                    status, progress, message, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    source_type.value,
                    source_label,
                    source_url,
                    source_path,
                    JobStatus.Queued.value,
                    0,
                    "Aguardando na fila.",
                    now,
                    now,
                ),
            )
        job = self.get_job(job_id)
        assert job is not None
        return job

    def get_job(self, job_id: str) -> Job | None:
        with self._lock:
            row = self._connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._map_job(row) if row is not None else None

    def list_jobs(self, *, limit: int = 100) -> list[Job]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC, rowid DESC LIMIT ?",
                (max(1, min(limit, 500)),),
            ).fetchall()
        return [self._map_job(row) for row in rows]

    def transition(
        self,
        job_id: str,
        status: JobStatus,
        *,
        message: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> Job:
        current = self._require_job(job_id)
        if status not in ALLOWED_JOB_TRANSITIONS[current.status]:
            raise RuneError(
                code="invalid_job_transition",
                message=f"Invalid job transition: {current.status.value} -> {status.value}",
            )

        now = _utc_now()
        started_at = current.started_at
        completed_at = current.completed_at
        progress = current.progress
        if started_at is None and status is not JobStatus.Queued:
            started_at = now
        if status is JobStatus.Completed:
            progress = 100
            completed_at = now
        elif status in {JobStatus.Failed, JobStatus.Cancelled}:
            completed_at = now

        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE jobs
                SET status = ?, progress = ?, message = ?, error_code = ?,
                    error_message = ?, updated_at = ?, started_at = ?, completed_at = ?
                WHERE id = ?
                """,
                (
                    status.value,
                    progress,
                    message or self._default_message(status),
                    error_code,
                    error_message,
                    now,
                    started_at,
                    completed_at,
                    job_id,
                ),
            )
        return self._require_job(job_id)

    def update_progress(self, job_id: str, *, progress: int, message: str) -> Job:
        self._require_job(job_id)
        clamped = max(0, min(progress, 100))
        with self._lock, self._connection:
            self._connection.execute(
                "UPDATE jobs SET progress = ?, message = ?, updated_at = ? WHERE id = ?",
                (clamped, message, _utc_now(), job_id),
            )
        return self._require_job(job_id)

    def update_media(
        self,
        job_id: str,
        *,
        title: str | None,
        duration: float | None,
        source_path: str | None = None,
    ) -> Job:
        self._require_job(job_id)
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE jobs
                SET media_title = COALESCE(?, media_title),
                    media_duration = COALESCE(?, media_duration),
                    source_path = COALESCE(?, source_path),
                    updated_at = ?
                WHERE id = ?
                """,
                (title, duration, source_path, _utc_now(), job_id),
            )
        return self._require_job(job_id)

    def recover_interrupted_jobs(self) -> int:
        active_values = tuple(status.value for status in ACTIVE_JOB_STATUSES)
        placeholders = ",".join("?" for _ in active_values)
        now = _utc_now()
        with self._lock, self._connection:
            cursor = self._connection.execute(
                f"""
                UPDATE jobs
                SET status = ?, progress = 0, message = ?, error_code = NULL,
                    error_message = NULL, updated_at = ?, started_at = NULL,
                    completed_at = NULL
                WHERE status IN ({placeholders})
                """,
                (
                    JobStatus.Queued.value,
                    "Retomado após reiniciar o Rune.",
                    now,
                    *active_values,
                ),
            )
        return cursor.rowcount

    def _require_job(self, job_id: str) -> Job:
        job = self.get_job(job_id)
        if job is None:
            raise RuneError(code="job_not_found", message="Job not found.")
        return job

    @staticmethod
    def _default_message(status: JobStatus) -> str:
        messages = {
            JobStatus.Queued: "Aguardando na fila.",
            JobStatus.Downloading: "Baixando mídia.",
            JobStatus.Preparing: "Preparando áudio.",
            JobStatus.Transcribing: "Transcrevendo.",
            JobStatus.Diarizing: "Separando vozes.",
            JobStatus.Finalizing: "Finalizando texto.",
            JobStatus.Completed: "Texto pronto.",
            JobStatus.Failed: "A transcrição precisa de atenção.",
            JobStatus.Cancelled: "Item cancelado.",
        }
        return messages[status]

    @staticmethod
    def _map_job(row: sqlite3.Row) -> Job:
        return Job(
            id=str(row["id"]),
            source_type=SourceType(str(row["source_type"])),
            source_label=str(row["source_label"]),
            source_url=str(row["source_url"]) if row["source_url"] is not None else None,
            source_path=str(row["source_path"]) if row["source_path"] is not None else None,
            status=JobStatus(str(row["status"])),
            progress=int(row["progress"]),
            message=str(row["message"]),
            error_code=str(row["error_code"]) if row["error_code"] is not None else None,
            error_message=(str(row["error_message"]) if row["error_message"] is not None else None),
            media_title=str(row["media_title"]) if row["media_title"] is not None else None,
            media_duration=(
                float(row["media_duration"]) if row["media_duration"] is not None else None
            ),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
            started_at=str(row["started_at"]) if row["started_at"] is not None else None,
            completed_at=(str(row["completed_at"]) if row["completed_at"] is not None else None),
        )
