import pytest

from app.core.errors import RuneError
from app.media.validation import validate_media_url, validate_upload_name


@pytest.mark.parametrize(
    "name",
    ["reuniao.mp3", "aula.MOV", "podcast.m4a", "captura.webm", "video.mp4"],
)
def test_common_audio_and_video_files_are_accepted(name: str) -> None:
    assert validate_upload_name(name) == name


def test_non_media_upload_is_rejected() -> None:
    with pytest.raises(RuneError, match="audio or video"):
        validate_upload_name("planilha.xlsx")


def test_only_http_links_are_accepted() -> None:
    assert validate_media_url("https://example.com/watch?v=1").startswith("https://")
    with pytest.raises(RuneError, match="HTTP"):
        validate_media_url("file:///Users/me/private.mp3")
