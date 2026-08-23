from dataclasses import dataclass

from app.jobs.enums import JobStatus, SourceType


@dataclass(frozen=True, slots=True)
class Job:
    id: str
    source_type: SourceType
    source_label: str
    source_url: str | None
    source_path: str | None
    status: JobStatus
    progress: int
    message: str
    error_code: str | None
    error_message: str | None
    media_title: str | None
    media_duration: float | None
    created_at: str
    updated_at: str
    started_at: str | None
    completed_at: str | None
