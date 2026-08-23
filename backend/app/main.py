from __future__ import annotations

import asyncio
import platform
import shutil
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import urlparse

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, Field

from app.core.errors import RuneError
from app.core.paths import RuntimePaths, build_runtime_paths, ensure_runtime_paths
from app.core.settings import Settings
from app.events.broker import EventBroker
from app.jobs.enums import JobStatus, SourceType
from app.jobs.repository import JobRepository
from app.jobs.scheduler import JobScheduler
from app.jobs.types import Job
from app.media.service import MediaService
from app.media.validation import validate_media_url, validate_upload_name
from app.transcription.mlx_engine import MlxWhisperEngine
from app.transcription.protocol import TranscriptionEngine
from app.transcripts.exports import EXPORT_FORMATS, render_export
from app.transcripts.repository import TranscriptRepository


class LinkBatch(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=50)


class TranscriptEdit(BaseModel):
    text: str = Field(max_length=5_000_000)


def _job_payload(job: Job) -> dict[str, object]:
    return {
        "id": job.id,
        "source_type": job.source_type.value,
        "source_label": job.source_label,
        "source_url": job.source_url,
        "status": job.status.value,
        "progress": job.progress,
        "message": job.message,
        "error_code": job.error_code,
        "error_message": job.error_message,
        "media_title": job.media_title,
        "media_duration": job.media_duration,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
    }


def _filename(job_label: str, export_format: str) -> str:
    stem = Path(job_label).stem.strip() or "transcript"
    safe = "".join(
        character if character.isalnum() or character in "-_ " else "-" for character in stem
    )
    return f"{safe.strip() or 'transcript'}.{export_format}"


def create_app(
    *,
    paths: RuntimePaths | None = None,
    settings: Settings | None = None,
    media: MediaService | None = None,
    engine: TranscriptionEngine | None = None,
) -> FastAPI:
    active_settings = settings or Settings()
    active_paths = paths or build_runtime_paths()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        ensured_paths = ensure_runtime_paths(active_paths)
        jobs = JobRepository(ensured_paths.database)
        transcripts = TranscriptRepository(ensured_paths.database)
        events = EventBroker()
        media_service = media or MediaService(
            cache_path=ensured_paths.cache,
            ffmpeg_binary=active_settings.ffmpeg_binary,
            ffprobe_binary=active_settings.ffprobe_binary,
            download_workers=active_settings.download_workers,
            preparation_workers=active_settings.preparation_workers,
        )
        transcription_engine = engine or MlxWhisperEngine(
            model=active_settings.whisper_model,
            models_path=ensured_paths.models,
        )
        scheduler = JobScheduler(
            jobs=jobs,
            transcripts=transcripts,
            media=media_service,
            engine=transcription_engine,
            events=events,
            library_path=ensured_paths.library,
            transcription_workers=active_settings.transcription_workers or 1,
        )
        application.state.paths = ensured_paths
        application.state.jobs = jobs
        application.state.transcripts = transcripts
        application.state.events = events
        application.state.scheduler = scheduler
        await scheduler.start()
        try:
            yield
        finally:
            await scheduler.stop()
            transcripts.close()
            jobs.close()

    application = FastAPI(
        title="Rune local API",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[active_settings.frontend_origin, "http://localhost:3000"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["*"],
    )

    allowed_origins = {active_settings.frontend_origin, "http://localhost:3000"}

    @application.middleware("http")
    async def protect_local_mutations(request: Request, call_next: Any) -> Response:
        origin = request.headers.get("origin")
        if (
            request.method in {"POST", "PATCH", "PUT", "DELETE"}
            and origin is not None
            and origin not in allowed_origins
        ):
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "code": "origin_not_allowed",
                        "message": "Esta ação só pode ser feita pela interface local do Rune.",
                    }
                },
            )
        response: Response = await call_next(request)
        return response

    @application.exception_handler(RuneError)
    async def rune_error_handler(_request: Request, error: RuneError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": {"code": error.code, "message": error.message}},
        )

    @application.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ready"}

    @application.get("/api/system")
    async def system(request: Request) -> dict[str, object]:
        runtime_paths: RuntimePaths = request.app.state.paths
        return {
            "privacy": "local_only",
            "platform": platform.machine(),
            "library_path": str(runtime_paths.library),
            "model": active_settings.whisper_model,
            "quality": active_settings.transcription_profile,
            "ffmpeg_ready": shutil.which(active_settings.ffmpeg_binary) is not None,
            "first_run_note": "O modelo é baixado uma vez na primeira transcrição.",
        }

    @application.get("/api/jobs")
    async def list_jobs(request: Request) -> list[dict[str, object]]:
        return [_job_payload(job) for job in request.app.state.jobs.list_jobs()]

    @application.get("/api/jobs/{job_id}")
    async def get_job(job_id: str, request: Request) -> dict[str, object]:
        job = request.app.state.jobs.get_job(job_id)
        if job is None:
            raise RuneError(code="job_not_found", message="Este item não existe mais.")
        return _job_payload(job)

    @application.post("/api/jobs/links", status_code=201)
    async def create_link_jobs(batch: LinkBatch, request: Request) -> list[dict[str, object]]:
        jobs = []
        for value in batch.urls:
            url = validate_media_url(value)
            host = urlparse(url).hostname or "Link"
            jobs.append(
                request.app.state.jobs.create_job(
                    source_type=SourceType.Link,
                    source_label=host.removeprefix("www."),
                    source_url=url,
                )
            )
        request.app.state.scheduler.notify()
        await request.app.state.events.publish()
        return [_job_payload(job) for job in jobs]

    @application.post("/api/jobs/uploads", status_code=201)
    async def create_upload_jobs(
        request: Request,
        files: Annotated[list[UploadFile], File(...)],
    ) -> list[dict[str, object]]:
        if len(files) > 50:
            raise RuneError(code="too_many_files", message="Adicione até 50 arquivos por vez.")
        jobs = []
        for upload in files:
            safe_name = validate_upload_name(upload.filename or "")
            job = request.app.state.jobs.create_job(
                source_type=SourceType.Upload,
                source_label=safe_name,
            )
            destination = request.app.state.paths.cache / "uploads" / job.id / safe_name
            destination.parent.mkdir(parents=True, exist_ok=True)
            try:
                with destination.open("wb") as output:
                    while chunk := await upload.read(1024 * 1024):
                        output.write(chunk)
            finally:
                await upload.close()
            job = request.app.state.jobs.update_media(
                job.id,
                title=Path(safe_name).stem,
                duration=None,
                source_path=str(destination),
            )
            jobs.append(job)
        request.app.state.scheduler.notify()
        await request.app.state.events.publish()
        return [_job_payload(job) for job in jobs]

    @application.post("/api/jobs/{job_id}/cancel")
    async def cancel_job(job_id: str, request: Request) -> dict[str, object]:
        job = request.app.state.jobs.get_job(job_id)
        if job is None:
            raise RuneError(code="job_not_found", message="Este item não existe mais.")
        if job.status in {JobStatus.Completed, JobStatus.Failed, JobStatus.Cancelled}:
            return _job_payload(job)
        updated = request.app.state.jobs.transition(job_id, JobStatus.Cancelled)
        await request.app.state.events.publish()
        return _job_payload(updated)

    @application.post("/api/jobs/{job_id}/retry")
    async def retry_job(job_id: str, request: Request) -> dict[str, object]:
        job = request.app.state.jobs.get_job(job_id)
        if job is None:
            raise RuneError(code="job_not_found", message="Este item não existe mais.")
        if job.status not in {JobStatus.Failed, JobStatus.Cancelled}:
            return _job_payload(job)
        updated = request.app.state.jobs.transition(job_id, JobStatus.Queued)
        request.app.state.scheduler.notify()
        await request.app.state.events.publish()
        return _job_payload(updated)

    @application.get("/api/jobs/{job_id}/transcript")
    async def get_transcript(job_id: str, request: Request) -> dict[str, Any]:
        repository: TranscriptRepository = request.app.state.transcripts
        transcript = repository.get(job_id)
        if transcript is None:
            raise RuneError(code="transcript_not_found", message="O texto ainda não está pronto.")
        return transcript.to_dict()

    @application.patch("/api/jobs/{job_id}/transcript")
    async def edit_transcript(
        job_id: str,
        edit: TranscriptEdit,
        request: Request,
    ) -> dict[str, Any]:
        repository: TranscriptRepository = request.app.state.transcripts
        transcript = repository.update_text(job_id, edit.text)
        await asyncio.to_thread(
            _rewrite_exports,
            transcript,
            request.app.state.paths.library,
        )
        return transcript.to_dict()

    @application.get("/api/jobs/{job_id}/export/{export_format}")
    async def export_transcript(job_id: str, export_format: str, request: Request) -> Response:
        if export_format not in EXPORT_FORMATS:
            raise RuneError(code="unsupported_export", message="Este formato não está disponível.")
        transcript = request.app.state.transcripts.get(job_id)
        job = request.app.state.jobs.get_job(job_id)
        if transcript is None or job is None:
            raise RuneError(code="transcript_not_found", message="O texto ainda não está pronto.")
        media_types = {
            "txt": "text/plain",
            "md": "text/markdown",
            "srt": "application/x-subrip",
            "vtt": "text/vtt",
            "json": "application/json",
        }
        download_name = _filename(job.media_title or job.source_label, export_format)
        return Response(
            render_export(transcript, export_format),
            media_type=f"{media_types[export_format]}; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
        )

    @application.get("/api/jobs/{job_id}/media")
    async def media_file(job_id: str, request: Request) -> FileResponse:
        job = request.app.state.jobs.get_job(job_id)
        if job is None or not job.source_path or not Path(job.source_path).is_file():
            raise RuneError(code="media_not_found", message="A mídia original não está disponível.")
        return FileResponse(job.source_path, filename=Path(job.source_path).name)

    @application.get("/api/events")
    async def events(request: Request) -> StreamingResponse:
        async def stream() -> AsyncIterator[str]:
            yield "event: ready\ndata: connected\n\n"
            async for event in request.app.state.events.subscribe():
                if await request.is_disconnected():
                    break
                if event == "heartbeat":
                    yield ": keepalive\n\n"
                else:
                    yield f"event: queue\ndata: {event}\n\n"

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return application


def _rewrite_exports(transcript: object, library_path: Path) -> None:
    from app.transcripts.writer import write_export_bundle

    write_export_bundle(transcript, library_path)  # type: ignore[arg-type]


app = create_app()
