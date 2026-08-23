from pathlib import Path
from urllib.parse import urlparse

from app.core.errors import RuneError

SUPPORTED_MEDIA_EXTENSIONS = frozenset(
    {
        ".aac",
        ".aiff",
        ".alac",
        ".avi",
        ".flac",
        ".m4a",
        ".mkv",
        ".mov",
        ".mp3",
        ".mp4",
        ".mpeg",
        ".mpg",
        ".oga",
        ".ogg",
        ".opus",
        ".wav",
        ".webm",
        ".wmv",
    }
)


def validate_upload_name(filename: str) -> str:
    safe_name = Path(filename).name.strip()
    if not safe_name or Path(safe_name).suffix.lower() not in SUPPORTED_MEDIA_EXTENSIONS:
        raise RuneError(
            code="unsupported_media",
            message="Rune accepts audio or video files in common formats.",
        )
    return safe_name


def validate_media_url(value: str) -> str:
    url = value.strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuneError(
            code="invalid_media_url",
            message="The media link must use HTTP or HTTPS.",
        )
    return url
