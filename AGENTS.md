# Rune workspace instructions

Rune is a local-only audio and video transcription application for Apple Silicon Macs.

## Product boundaries

- All media processing and transcription happen on the user's Mac.
- Do not add paid APIs, hosted transcription, authentication, analytics, or public deployment assumptions.
- The browser UI is Next.js. The loopback service is FastAPI.
- The backend binds to `127.0.0.1` by default.
- Runtime data belongs outside the repository under Documents, Application Support, and Caches.
- Source code, comments, technical documentation, and commits are written in English.
- User-facing interface copy is Brazilian Portuguese.

## Repository map

- `frontend/`: Next.js App Router interface and frontend knowledge base.
- `backend/`: FastAPI API, queue, media processing, transcription, persistence, and exports.
- `Makefile`: root install, start, and verification commands.
- `.superpowers/`: local planning and visual artifacts; never versioned.
- `/docs/`: never versioned in this repository.

## Required commands

- `make install`: install frontend and backend dependencies.
- `make start`: start both local services.
- `make check`: run the complete frontend and backend quality gate.

## Implementation rules

- Follow test-driven development for behavior changes.
- Keep media, queue, storage, and transcription behind explicit interfaces.
- Never interpolate user-controlled values into shell command strings.
- Preserve original media and raw engine output when editable transcripts change.
- Model loading must remain lazy so tests and API startup do not download model weights.
- A failed job must not interrupt the rest of the queue.
- Keep components and Python modules focused on one responsibility.
- Prefer platform APIs and the standard library before adding dependencies.

Read `frontend/AGENTS.md` before frontend changes and `backend/AGENTS.md` before backend changes.
