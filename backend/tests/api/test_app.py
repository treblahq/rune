from pathlib import Path

from fastapi.testclient import TestClient

from app.core.paths import RuntimePaths
from app.core.settings import Settings
from app.main import create_app
from app.media.types import PreparedMedia
from app.transcripts.types import Segment, Transcript


class FakeMediaService:
    async def prepare(
        self, job_id: str, source_path: str | None, source_url: str | None
    ) -> PreparedMedia:
        del source_path, source_url
        return PreparedMedia(Path(f"/tmp/{job_id}.wav"), "Mídia teste", 1.0, None)


class FakeEngine:
    async def transcribe(self, job_id: str, audio_path: Path) -> Transcript:
        del audio_path
        return Transcript(
            job_id=job_id,
            text="Tudo certo.",
            language="pt",
            duration=1.0,
            segments=(Segment(id=0, start=0, end=1, text="Tudo certo."),),
        )


def build_paths(tmp_path: Path) -> RuntimePaths:
    return RuntimePaths(
        library=tmp_path / "library",
        state=tmp_path / "state",
        cache=tmp_path / "cache",
        models=tmp_path / "models",
        database=tmp_path / "state" / "rune.sqlite3",
    )


def test_health_and_system_are_local_first(tmp_path: Path) -> None:
    app = create_app(
        paths=build_paths(tmp_path),
        settings=Settings(),
        media=FakeMediaService(),  # type: ignore[arg-type]
        engine=FakeEngine(),  # type: ignore[arg-type]
    )

    with TestClient(app) as client:
        health = client.get("/api/health")
        system = client.get("/api/system")

    assert health.json() == {"status": "ready"}
    assert system.json()["privacy"] == "local_only"
    assert system.json()["library_path"].endswith("library")


def test_links_are_added_as_independent_queue_items(tmp_path: Path) -> None:
    app = create_app(
        paths=build_paths(tmp_path),
        settings=Settings(),
        media=FakeMediaService(),  # type: ignore[arg-type]
        engine=FakeEngine(),  # type: ignore[arg-type]
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/jobs/links",
            json={"urls": ["https://example.com/a", "https://example.com/b"]},
        )
        jobs = client.get("/api/jobs").json()

    assert response.status_code == 201
    assert len(response.json()) == 2
    assert len(jobs) == 2
    assert {job["source_type"] for job in jobs} == {"link"}


def test_invalid_link_returns_human_error(tmp_path: Path) -> None:
    app = create_app(
        paths=build_paths(tmp_path),
        settings=Settings(),
        media=FakeMediaService(),  # type: ignore[arg-type]
        engine=FakeEngine(),  # type: ignore[arg-type]
    )

    with TestClient(app) as client:
        response = client.post("/api/jobs/links", json={"urls": ["file:///secret.mp3"]})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_media_url"


def test_upload_is_saved_outside_project_and_queued(tmp_path: Path) -> None:
    paths = build_paths(tmp_path)
    app = create_app(
        paths=paths,
        settings=Settings(),
        media=FakeMediaService(),  # type: ignore[arg-type]
        engine=FakeEngine(),  # type: ignore[arg-type]
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/jobs/uploads",
            files=[("files", ("voice.mp3", b"fake audio", "audio/mpeg"))],
        )

    assert response.status_code == 201
    job_id = response.json()[0]["id"]
    assert (paths.cache / "uploads" / job_id / "voice.mp3").read_bytes() == b"fake audio"


def test_mutations_from_other_websites_are_rejected(tmp_path: Path) -> None:
    app = create_app(
        paths=build_paths(tmp_path),
        settings=Settings(),
        media=FakeMediaService(),  # type: ignore[arg-type]
        engine=FakeEngine(),  # type: ignore[arg-type]
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/jobs/links",
            json={"urls": ["https://example.com/video"]},
            headers={"Origin": "https://malicious.example"},
        )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "origin_not_allowed"
