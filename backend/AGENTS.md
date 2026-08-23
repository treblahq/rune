# Rune backend instructions

The backend is a loopback-only FastAPI service for local media transcription.

## Boundaries

- Bind to `127.0.0.1` unless an explicit local override is provided.
- Store jobs and transcripts in SQLite outside the repository.
- Store user exports under `~/Documents/Rune` by default.
- Keep media, queue, storage, and transcription behind protocols or focused functions.
- Load MLX and model weights lazily.
- Use subprocess argument arrays and never `shell=True` for user-controlled input.
- Preserve original media and raw engine output.
- Emit safe error codes and messages; do not expose command output by default.

## Code style

- Python 3.13.
- Type all public functions.
- Prefer dataclasses, enums, protocols, and plain functions over custom framework abstractions.
- Keep modules and functions focused on one responsibility.
- Use UTC ISO timestamps at storage and API boundaries.
- Code, comments, tests, docs, and commits are English.

## Testing

Use TDD. Tests inject fake downloader, media, and transcription adapters. Normal
API and unit tests must never download a model or access the public internet.

Run:

```bash
make test
make check
```
