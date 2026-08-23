from app.core.settings import Settings


def test_settings_bind_to_loopback_by_default() -> None:
    settings = Settings()

    assert settings.host == "127.0.0.1"
    assert settings.port == 43891
    assert settings.frontend_origin == "http://127.0.0.1:3000"


def test_settings_use_maximum_quality_model_by_default() -> None:
    settings = Settings()

    assert settings.whisper_model == "mlx-community/whisper-large-v3-mlx"
    assert settings.transcription_profile == "maximum"
