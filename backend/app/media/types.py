from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PreparedMedia:
    path: Path
    title: str
    duration: float | None
    original_path: Path | None
