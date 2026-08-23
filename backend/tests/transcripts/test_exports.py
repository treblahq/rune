import json

from app.transcripts.exports import render_export
from tests.transcripts.test_repository import sample_transcript


def test_txt_and_markdown_exports_use_edited_text() -> None:
    transcript = sample_transcript()
    transcript = transcript.with_text("Texto revisado.")

    assert render_export(transcript, "txt") == "Texto revisado.\n"
    assert "# Transcrição" in render_export(transcript, "md")
    assert "Texto revisado." in render_export(transcript, "md")


def test_subtitle_exports_use_timed_segments() -> None:
    transcript = sample_transcript()

    assert "00:00:00,000 --> 00:00:01,400" in render_export(transcript, "srt")
    assert "00:00:00.000 --> 00:00:01.400" in render_export(transcript, "vtt")


def test_json_export_includes_low_confidence_words() -> None:
    payload = json.loads(render_export(sample_transcript(), "json"))

    assert payload["language"] == "pt"
    assert payload["segments"][0]["words"][1]["confidence"] == 0.42
