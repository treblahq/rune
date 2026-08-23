from pathlib import Path

import pytest

from app.core.errors import RuneError
from app.jobs.enums import JobStatus, SourceType
from app.jobs.repository import JobRepository


def test_active_job_is_requeued_after_restart(tmp_path: Path) -> None:
    repository = JobRepository(tmp_path / "rune.sqlite3")
    job = repository.create_job(source_type=SourceType.Upload, source_label="audio.m4a")
    repository.transition(job.id, JobStatus.Preparing)
    repository.transition(job.id, JobStatus.Transcribing)

    recovered_count = repository.recover_interrupted_jobs()

    recovered = repository.get_job(job.id)
    assert recovered_count == 1
    assert recovered is not None
    assert recovered.status is JobStatus.Queued
    assert recovered.message == "Retomado após reiniciar o Rune."


def test_completed_job_is_not_requeued(tmp_path: Path) -> None:
    repository = JobRepository(tmp_path / "rune.sqlite3")
    job = repository.create_job(source_type=SourceType.Upload, source_label="audio.m4a")
    for status in (
        JobStatus.Preparing,
        JobStatus.Transcribing,
        JobStatus.Finalizing,
        JobStatus.Completed,
    ):
        repository.transition(job.id, status)

    recovered_count = repository.recover_interrupted_jobs()

    assert recovered_count == 0
    assert repository.get_job(job.id).status is JobStatus.Completed  # type: ignore[union-attr]


def test_invalid_transition_is_rejected(tmp_path: Path) -> None:
    repository = JobRepository(tmp_path / "rune.sqlite3")
    job = repository.create_job(source_type=SourceType.Link, source_label="episode")

    with pytest.raises(RuneError, match="Invalid job transition") as error:
        repository.transition(job.id, JobStatus.Completed)

    assert error.value.code == "invalid_job_transition"


def test_finalizing_job_can_still_be_cancelled(tmp_path: Path) -> None:
    repository = JobRepository(tmp_path / "rune.sqlite3")
    job = repository.create_job(source_type=SourceType.Upload, source_label="sample.wav")
    repository.transition(job.id, JobStatus.Preparing)
    repository.transition(job.id, JobStatus.Transcribing)
    repository.transition(job.id, JobStatus.Finalizing)

    cancelled = repository.transition(job.id, JobStatus.Cancelled)

    assert cancelled.status is JobStatus.Cancelled
