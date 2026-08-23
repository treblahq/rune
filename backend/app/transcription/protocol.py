from pathlib import Path
from typing import Protocol

from app.transcripts.types import Transcript


class TranscriptionEngine(Protocol):
    async def transcribe(self, job_id: str, audio_path: Path) -> Transcript: ...
