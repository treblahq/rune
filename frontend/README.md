# Rune frontend

The Rune frontend is a Next.js App Router interface for the local FastAPI
transcription service. It is not deployed publicly and does not process media.

## Commands

```bash
make install
make dev
make check
```

The local API defaults to `http://127.0.0.1:43891` and can be overridden with
`NEXT_PUBLIC_RUNE_API_URL`.

Read `AGENTS.md` and `.knowledge/README.md` before changing the interface.
