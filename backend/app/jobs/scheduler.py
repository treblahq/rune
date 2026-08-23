from __future__ import annotations

import asyncio
from contextlib import suppress
from pathlib import Path

from app.core.errors import RuneError
from app.events.broker import EventBroker
from app.jobs.enums import JobStatus, SourceType
from app.jobs.repository import JobRepository
from app.media.service import MediaService
from app.transcription.protocol import TranscriptionEngine
from app.transcripts.repository import TranscriptRepository
from app.transcripts.writer import write_export_bundle


class JobScheduler:
    def __init__(
        self,
        *,
        jobs: JobRepository,
        transcripts: TranscriptRepository,
        media: MediaService,
        engine: TranscriptionEngine,
        events: EventBroker,
        library_path: Path,
        transcription_workers: int = 1,
        max_inflight: int = 8,
    ) -> None:
        self._jobs = jobs
        self._transcripts = transcripts
        self._media = media
        self._engine = engine
        self._events = events
        self._library_path = library_path
        self._transcription_semaphore = asyncio.Semaphore(transcription_workers)
        self._max_inflight = max_inflight
        self._running: dict[str, asyncio.Task[None]] = {}
        self._wake = asyncio.Event()
        self._loop_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self._jobs.recover_interrupted_jobs()
        self._loop_task = asyncio.create_task(self._run_loop(), name="rune-scheduler")
        self.notify()

    async def stop(self) -> None:
        if self._loop_task:
            self._loop_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._loop_task
        if self._running:
            for task in self._running.values():
                task.cancel()
            await asyncio.gather(*self._running.values(), return_exceptions=True)
            self._running.clear()

    def notify(self) -> None:
        self._wake.set()

    async def _run_loop(self) -> None:
        while True:
            self._remove_finished()
            available = self._max_inflight - len(self._running)
            if available > 0:
                queued = [
                    job
                    for job in reversed(self._jobs.list_jobs(limit=500))
                    if job.status is JobStatus.Queued and job.id not in self._running
                ]
                for job in queued[:available]:
                    self._running[job.id] = asyncio.create_task(
                        self.process_job(job.id), name=f"rune-job-{job.id}"
                    )
            self._wake.clear()
            with suppress(TimeoutError):
                await asyncio.wait_for(self._wake.wait(), timeout=0.75)

    def _remove_finished(self) -> None:
        for job_id, task in tuple(self._running.items()):
            if task.done():
                self._running.pop(job_id, None)

    async def process_job(self, job_id: str) -> None:
        job = self._jobs.get_job(job_id)
        if job is None or job.status is not JobStatus.Queued:
            return
        try:
            if job.source_type is SourceType.Link:
                self._jobs.transition(job.id, JobStatus.Downloading)
                await self._changed()
            else:
                self._jobs.transition(job.id, JobStatus.Preparing)
                await self._changed()

            media = await self._media.prepare(job.id, job.source_path, job.source_url)
            current = self._jobs.get_job(job.id)
            if current is None or current.status is JobStatus.Cancelled:
                return
            if current.status is JobStatus.Downloading:
                self._jobs.transition(job.id, JobStatus.Preparing)
            self._jobs.update_media(
                job.id,
                title=media.title,
                duration=media.duration,
                source_path=str(media.original_path) if media.original_path else None,
            )
            self._jobs.update_progress(
                job.id, progress=24, message="Áudio pronto para transcrever."
            )
            await self._changed()

            async with self._transcription_semaphore:
                current = self._jobs.get_job(job.id)
                if current is None or current.status is JobStatus.Cancelled:
                    return
                self._jobs.transition(job.id, JobStatus.Transcribing)
                self._jobs.update_progress(
                    job.id,
                    progress=32,
                    message="O Rune está ouvindo com atenção.",
                )
                await self._changed()
                transcript = await self._engine.transcribe(job.id, media.path)

            self._jobs.transition(job.id, JobStatus.Finalizing)
            self._jobs.update_progress(job.id, progress=92, message="Organizando o texto.")
            self._transcripts.save(transcript)
            await asyncio.to_thread(write_export_bundle, transcript, self._library_path)
            self._jobs.transition(job.id, JobStatus.Completed)
            await self._changed()
        except asyncio.CancelledError:
            raise
        except Exception as error:
            current = self._jobs.get_job(job.id)
            if current is not None and current.status not in {
                JobStatus.Completed,
                JobStatus.Cancelled,
                JobStatus.Failed,
            }:
                code = error.code if isinstance(error, RuneError) else "transcription_failed"
                message = (
                    error.message
                    if isinstance(error, RuneError)
                    else "Não foi possível concluir este item. Os outros continuam normalmente."
                )
                self._jobs.transition(
                    job.id,
                    JobStatus.Failed,
                    message="Este item precisa de atenção.",
                    error_code=code,
                    error_message=message,
                )
                await self._changed()

    async def _changed(self) -> None:
        await self._events.publish()
