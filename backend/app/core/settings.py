from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RUNE_", extra="ignore")

    host: str = "127.0.0.1"
    port: int = Field(default=43891, ge=1, le=65535)
    frontend_origin: str = "http://127.0.0.1:3000"
    whisper_model: str = "mlx-community/whisper-large-v3-mlx"
    transcription_profile: Literal["maximum", "faster"] = "maximum"
    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"
    download_workers: int = Field(default=3, ge=1, le=8)
    preparation_workers: int = Field(default=2, ge=1, le=4)
    transcription_workers: int | None = Field(default=None, ge=1, le=2)
