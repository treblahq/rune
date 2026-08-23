from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RuntimePaths:
    library: Path
    state: Path
    cache: Path
    models: Path
    database: Path


def _path_from_environment(name: str, fallback: Path) -> Path:
    configured = os.getenv(name, "").strip()
    return Path(configured).expanduser() if configured else fallback


def build_runtime_paths() -> RuntimePaths:
    home = Path(os.getenv("RUNE_HOME", "~")).expanduser()
    state = _path_from_environment(
        "RUNE_STATE_DIR",
        home / "Library" / "Application Support" / "Rune",
    )
    library = _path_from_environment("RUNE_LIBRARY_DIR", home / "Documents" / "Rune")
    cache = _path_from_environment("RUNE_CACHE_DIR", home / "Library" / "Caches" / "Rune")
    models = _path_from_environment("RUNE_MODELS_DIR", state / "models")
    database = _path_from_environment("RUNE_DATABASE_PATH", state / "rune.sqlite3")
    return RuntimePaths(
        library=library,
        state=state,
        cache=cache,
        models=models,
        database=database,
    )


def ensure_runtime_paths(paths: RuntimePaths) -> RuntimePaths:
    for path in (paths.library, paths.state, paths.cache, paths.models, paths.database.parent):
        path.mkdir(parents=True, exist_ok=True)
    return paths
