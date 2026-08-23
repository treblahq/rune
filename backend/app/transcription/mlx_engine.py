from __future__ import annotations

import asyncio
import math
from pathlib import Path
from typing import Any

from app.transcripts.types import Segment, Transcript, Word


def _number(value: Any, fallback: float = 0.0) -> float:
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else fallback
    except (TypeError, ValueError):
        return fallback


def transcript_from_mlx_result(job_id: str, result: dict[str, Any]) -> Transcript:
    segments: list[Segment] = []
    for index, raw_segment in enumerate(result.get("segments") or []):
        words = tuple(
            Word(
                text=str(raw_word.get("word", "")),
                start=_number(raw_word.get("start")),
                end=_number(raw_word.get("end")),
                confidence=(
                    _number(raw_word.get("probability"))
                    if raw_word.get("probability") is not None
                    else None
                ),
            )
            for raw_word in (raw_segment.get("words") or [])
        )
        segments.append(
            Segment(
                id=int(raw_segment.get("id", index)),
                start=_number(raw_segment.get("start")),
                end=_number(raw_segment.get("end")),
                text=str(raw_segment.get("text", "")).strip(),
                words=words,
            )
        )
    duration = max((segment.end for segment in segments), default=0.0) or None
    language = result.get("language")
    return Transcript(
        job_id=job_id,
        text=str(result.get("text", "")).strip(),
        language=str(language) if language else None,
        duration=duration,
        segments=tuple(segments),
    )


class MlxWhisperEngine:
    def __init__(self, *, model: str) -> None:
        self._model = model

    async def transcribe(self, job_id: str, audio_path: Path) -> Transcript:
        result = await asyncio.to_thread(self._transcribe_sync, audio_path)
        return transcript_from_mlx_result(job_id, result)

    def _transcribe_sync(self, audio_path: Path) -> dict[str, Any]:
        import mlx_whisper

        result: dict[str, Any] = mlx_whisper.transcribe(
            str(audio_path),
            path_or_hf_repo=self._model,
            word_timestamps=True,
            verbose=False,
        )
        return result
