from pathlib import Path

from app.transcripts.exports import EXPORT_FORMATS, render_export
from app.transcripts.types import Transcript


def write_export_bundle(transcript: Transcript, library_path: Path) -> Path:
    destination = library_path / transcript.job_id
    destination.mkdir(parents=True, exist_ok=True)
    for export_format in EXPORT_FORMATS:
        (destination / f"transcript.{export_format}").write_text(
            render_export(transcript, export_format), encoding="utf-8"
        )
    return destination
