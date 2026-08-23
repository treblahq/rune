from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any

import yt_dlp

from app.core.errors import RuneError
from app.media.types import PreparedMedia


class MediaService:
    def __init__(
        self,
        *,
        cache_path: Path,
        ffmpeg_binary: str,
        ffprobe_binary: str,
        download_workers: int = 3,
        preparation_workers: int = 2,
    ) -> None:
        self._jobs_path = cache_path / "jobs"
        self._jobs_path.mkdir(parents=True, exist_ok=True)
        self._ffmpeg = ffmpeg_binary
        self._ffprobe = ffprobe_binary
        self._download_semaphore = asyncio.Semaphore(download_workers)
        self._preparation_semaphore = asyncio.Semaphore(preparation_workers)

    async def prepare(
        self,
        job_id: str,
        source_path: str | None,
        source_url: str | None,
    ) -> PreparedMedia:
        job_path = self._jobs_path / job_id
        job_path.mkdir(parents=True, exist_ok=True)
        title: str
        original: Path
        if source_url:
            async with self._download_semaphore:
                original, title = await asyncio.to_thread(self._download, source_url, job_path)
        elif source_path:
            original = Path(source_path)
            title = original.stem
        else:
            raise RuneError(code="missing_media", message="No media source was provided.")

        if not original.exists():
            raise RuneError(
                code="media_missing", message="The original media file could not be found."
            )

        prepared = job_path / "prepared.wav"
        async with self._preparation_semaphore:
            await asyncio.to_thread(self._prepare_audio, original, prepared)
            duration = await asyncio.to_thread(self._duration, prepared)
        return PreparedMedia(
            path=prepared,
            title=title,
            duration=duration,
            original_path=original,
        )

    @staticmethod
    def _download(url: str, destination: Path) -> tuple[Path, str]:
        options: dict[str, Any] = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "outtmpl": str(destination / "source.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "restrictfilenames": True,
        }
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
                filename = Path(downloader.prepare_filename(info))
        except Exception as error:
            raise RuneError(
                code="download_failed",
                message="Rune could not download this link. Check the address and try again.",
            ) from error
        title = str(info.get("title") or filename.stem)
        return filename, title

    def _prepare_audio(self, source: Path, destination: Path) -> None:
        command = [
            self._ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(destination),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except (OSError, subprocess.CalledProcessError) as error:
            raise RuneError(
                code="media_preparation_failed",
                message="Rune could not prepare the audio from this item.",
            ) from error

    def _duration(self, source: Path) -> float | None:
        command = [
            self._ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(source),
        ]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            payload = json.loads(result.stdout)
            return float(payload["format"]["duration"])
        except (OSError, subprocess.CalledProcessError, KeyError, TypeError, ValueError):
            return None
