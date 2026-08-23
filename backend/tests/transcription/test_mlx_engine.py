from app.transcription.mlx_engine import transcript_from_mlx_result


def test_mlx_result_becomes_editable_timed_transcript() -> None:
    result = {
        "text": " Olá Rune. ",
        "language": "pt",
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 1.2,
                "text": " Olá Rune.",
                "words": [
                    {"word": " Olá", "start": 0.0, "end": 0.4, "probability": 0.97},
                    {"word": " Rune.", "start": 0.4, "end": 1.2, "probability": 0.61},
                ],
            }
        ],
    }

    transcript = transcript_from_mlx_result("job-1", result)

    assert transcript.text == "Olá Rune."
    assert transcript.duration == 1.2
    assert transcript.segments[0].words[1].confidence == 0.61
