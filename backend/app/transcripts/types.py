from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any


@dataclass(frozen=True, slots=True)
class Word:
    text: str
    start: float
    end: float
    confidence: float | None = None


@dataclass(frozen=True, slots=True)
class Segment:
    id: int
    start: float
    end: float
    text: str
    words: tuple[Word, ...] = ()
    speaker: str | None = None


@dataclass(frozen=True, slots=True)
class Transcript:
    job_id: str
    text: str
    language: str | None
    duration: float | None
    segments: tuple[Segment, ...]

    def with_text(self, text: str) -> Transcript:
        return replace(self, text=text)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Transcript:
        segments = tuple(
            Segment(
                id=int(segment["id"]),
                start=float(segment["start"]),
                end=float(segment["end"]),
                text=str(segment["text"]),
                speaker=str(segment["speaker"]) if segment.get("speaker") else None,
                words=tuple(
                    Word(
                        text=str(word["text"]),
                        start=float(word["start"]),
                        end=float(word["end"]),
                        confidence=(
                            float(word["confidence"])
                            if word.get("confidence") is not None
                            else None
                        ),
                    )
                    for word in segment.get("words", [])
                ),
            )
            for segment in payload.get("segments", [])
        )
        return cls(
            job_id=str(payload["job_id"]),
            text=str(payload.get("text", "")),
            language=str(payload["language"]) if payload.get("language") else None,
            duration=float(payload["duration"]) if payload.get("duration") is not None else None,
            segments=segments,
        )
