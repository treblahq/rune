from __future__ import annotations

import json
from typing import Literal

from app.core.errors import RuneError
from app.transcripts.types import Transcript

ExportFormat = Literal["txt", "md", "srt", "vtt", "json"]
EXPORT_FORMATS: tuple[ExportFormat, ...] = ("txt", "md", "srt", "vtt", "json")


def _timestamp(value: float, *, decimal: str) -> str:
    total_milliseconds = max(0, round(value * 1000))
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}{decimal}{milliseconds:03}"


def _subtitles(transcript: Transcript, *, webvtt: bool) -> str:
    decimal = "." if webvtt else ","
    blocks: list[str] = ["WEBVTT\n"] if webvtt else []
    for index, segment in enumerate(transcript.segments, start=1):
        prefix = "" if webvtt else f"{index}\n"
        speaker = f"{segment.speaker}: " if segment.speaker else ""
        blocks.append(
            f"{prefix}{_timestamp(segment.start, decimal=decimal)} --> "
            f"{_timestamp(segment.end, decimal=decimal)}\n{speaker}{segment.text.strip()}\n"
        )
    return "\n".join(blocks).rstrip() + "\n"


def render_export(transcript: Transcript, export_format: str) -> str:
    if export_format == "txt":
        return transcript.text.strip() + "\n"
    if export_format == "md":
        return f"# Transcrição\n\n{transcript.text.strip()}\n"
    if export_format == "srt":
        return _subtitles(transcript, webvtt=False)
    if export_format == "vtt":
        return _subtitles(transcript, webvtt=True)
    if export_format == "json":
        return json.dumps(transcript.to_dict(), ensure_ascii=False, indent=2) + "\n"
    raise RuneError(code="unsupported_export", message="Unsupported export format.")
