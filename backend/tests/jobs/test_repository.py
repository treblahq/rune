from pathlib import Path

from app.jobs.enums import JobStatus, SourceType
from app.jobs.repository import JobRepository


def test_created_job_survives_repository_reopen(tmp_path: Path) -> None:
    database_path = tmp_path / "rune.sqlite3"
    repository = JobRepository(database_path)
    created = repository.create_job(
        source_type=SourceType.Upload,
        source_label="meeting.m4a",
        source_path=str(tmp_path / "meeting.m4a"),
    )
    repository.close()

    reopened = JobRepository(database_path)
    loaded = reopened.get_job(created.id)

    assert loaded is not None
    assert loaded.id == created.id
    assert loaded.status is JobStatus.Queued
    assert loaded.source_label == "meeting.m4a"
    assert loaded.source_type is SourceType.Upload


def test_jobs_are_listed_newest_first(tmp_path: Path) -> None:
    repository = JobRepository(tmp_path / "rune.sqlite3")
    first = repository.create_job(source_type=SourceType.Link, source_label="first")
    second = repository.create_job(source_type=SourceType.Link, source_label="second")

    jobs = repository.list_jobs()

    assert [job.id for job in jobs] == [second.id, first.id]


def test_job_progress_is_clamped_and_persisted(tmp_path: Path) -> None:
    repository = JobRepository(tmp_path / "rune.sqlite3")
    job = repository.create_job(source_type=SourceType.Upload, source_label="audio.wav")

    updated = repository.update_progress(job.id, progress=140, message="Working")

    assert updated.progress == 100
    assert repository.get_job(job.id).message == "Working"  # type: ignore[union-attr]
