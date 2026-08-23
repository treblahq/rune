from pathlib import Path

from app.core.paths import build_runtime_paths, ensure_runtime_paths


def test_runtime_paths_stay_outside_repository(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("RUNE_HOME", str(tmp_path))

    paths = build_runtime_paths()

    assert paths.library == tmp_path / "Documents" / "Rune"
    assert paths.state == tmp_path / "Library" / "Application Support" / "Rune"
    assert paths.models == paths.state / "models"
    assert paths.cache == tmp_path / "Library" / "Caches" / "Rune"
    assert paths.database == paths.state / "rune.sqlite3"


def test_runtime_paths_allow_explicit_library_override(tmp_path: Path, monkeypatch) -> None:
    custom_library = tmp_path / "Transcripts"
    monkeypatch.setenv("RUNE_HOME", str(tmp_path))
    monkeypatch.setenv("RUNE_LIBRARY_DIR", str(custom_library))

    paths = build_runtime_paths()

    assert paths.library == custom_library


def test_ensure_runtime_paths_creates_required_directories(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("RUNE_HOME", str(tmp_path))

    paths = ensure_runtime_paths(build_runtime_paths())

    assert paths.library.is_dir()
    assert paths.state.is_dir()
    assert paths.models.is_dir()
    assert paths.cache.is_dir()
