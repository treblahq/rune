import asyncio
from pathlib import Path

import pytest

from app.events.broker import EventBroker
from app.jobs.enums import JobStatus, SourceType
from app.jobs.repository import JobRepository
from app.jobs.scheduler import JobScheduler
from app.media.types import PreparedMedia
from app.transcripts.repository import TranscriptRepository
from app.transcripts.types import Segment, Transcript


class FakeMediaService:
    async def prepare(
        self, job_id: str, source_path: str | None, source_url: str | None
    ) -> PreparedMedia:
        del source_path, source_url
        return PreparedMedia(
            path=Path(f"/tmp/{job_id}.wav"), title="Teste", duration=2.0, original_path=None
        )


class FakeEngine:
    async def transcribe(self, job_id: str, audio_path: Path) -> Transcript:
        del audio_path
        return Transcript(
            job_id=job_id,
            text="Texto pronto.",
            language="pt",
            duration=2.0,
            segments=(Segment(id=0, start=0.0, end=2.0, text="Texto pronto."),),
        )


@pytest.mark.asyncio
async def test_scheduler_completes_job_and_persists_transcript(tmp_path: Path) -> None:
    jobs = JobRepository(tmp_path / "rune.sqlite3")
    transcripts = TranscriptRepository(tmp_path / "rune.sqlite3")
    job = jobs.create_job(
        source_type=SourceType.Upload,
        source_label="teste.wav",
        source_path=str(tmp_path / "teste.wav"),
    )
    scheduler = JobScheduler(
        jobs=jobs,
        transcripts=transcripts,
        media=FakeMediaService(),  # type: ignore[arg-type]
        engine=FakeEngine(),  # type: ignore[arg-type]
        events=EventBroker(),
        library_path=tmp_path / "library",
    )

    await scheduler.process_job(job.id)

    completed = jobs.get_job(job.id)
    assert completed is not None
    assert completed.status is JobStatus.Completed
    assert transcripts.get(job.id).text == "Texto pronto."  # type: ignore[union-attr]
    assert (tmp_path / "library" / job.id / "transcript.txt").exists()
    jobs.close()
    transcripts.close()


@pytest.mark.asyncio
async def test_one_failed_job_does_not_change_other_queued_jobs(tmp_path: Path) -> None:
    class BrokenEngine:
        async def transcribe(self, job_id: str, audio_path: Path) -> Transcript:
            del job_id, audio_path
            raise RuntimeError("boom")

    jobs = JobRepository(tmp_path / "rune.sqlite3")
    transcripts = TranscriptRepository(tmp_path / "rune.sqlite3")
    first = jobs.create_job(source_type=SourceType.Upload, source_label="a.wav", source_path="a")
    second = jobs.create_job(source_type=SourceType.Upload, source_label="b.wav", source_path="b")
    scheduler = JobScheduler(
        jobs=jobs,
        transcripts=transcripts,
        media=FakeMediaService(),  # type: ignore[arg-type]
        engine=BrokenEngine(),  # type: ignore[arg-type]
        events=EventBroker(),
        library_path=tmp_path / "library",
    )

    await scheduler.process_job(first.id)

    assert jobs.get_job(first.id).status is JobStatus.Failed  # type: ignore[union-attr]
    assert jobs.get_job(second.id).status is JobStatus.Queued  # type: ignore[union-attr]
    jobs.close()
    transcripts.close()


@pytest.mark.asyncio
async def test_scheduler_stops_without_waiting_for_long_transcription(tmp_path: Path) -> None:
    started = asyncio.Event()
    never_finishes = asyncio.Event()

    class BlockingEngine:
        async def transcribe(self, job_id: str, audio_path: Path) -> Transcript:
            del job_id, audio_path
            started.set()
            await never_finishes.wait()
            raise AssertionError("unreachable")

    jobs = JobRepository(tmp_path / "rune.sqlite3")
    transcripts = TranscriptRepository(tmp_path / "rune.sqlite3")
    jobs.create_job(source_type=SourceType.Upload, source_label="long.wav", source_path="long")
    scheduler = JobScheduler(
        jobs=jobs,
        transcripts=transcripts,
        media=FakeMediaService(),  # type: ignore[arg-type]
        engine=BlockingEngine(),  # type: ignore[arg-type]
        events=EventBroker(),
        library_path=tmp_path / "library",
    )

    await scheduler.start()
    await asyncio.wait_for(started.wait(), timeout=0.2)
    await asyncio.wait_for(scheduler.stop(), timeout=0.2)

    assert jobs.list_jobs()[0].status is JobStatus.Transcribing
    jobs.close()
    transcripts.close()
