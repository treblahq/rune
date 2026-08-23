from pathlib import Path

from app.transcripts.repository import TranscriptRepository
from app.transcripts.types import Segment, Transcript, Word


def sample_transcript(job_id: str = "job-1") -> Transcript:
    return Transcript(
        job_id=job_id,
        text="Olá mundo.",
        language="pt",
        duration=1.4,
        segments=(
            Segment(
                id=0,
                start=0.0,
                end=1.4,
                text="Olá mundo.",
                words=(
                    Word(text="Olá", start=0.0, end=0.5, confidence=0.98),
                    Word(text=" mundo.", start=0.5, end=1.4, confidence=0.42),
                ),
            ),
        ),
    )


def test_transcript_round_trip_preserves_word_timestamps(tmp_path: Path) -> None:
    repository = TranscriptRepository(tmp_path / "rune.sqlite3")
    repository.save(sample_transcript())

    stored = repository.get("job-1")

    assert stored == sample_transcript()
    repository.close()


def test_edit_only_changes_visible_text(tmp_path: Path) -> None:
    repository = TranscriptRepository(tmp_path / "rune.sqlite3")
    repository.save(sample_transcript())

    edited = repository.update_text("job-1", "Olá, Rune.")

    assert edited.text == "Olá, Rune."
    assert edited.segments[0].words[1].confidence == 0.42
    repository.close()
