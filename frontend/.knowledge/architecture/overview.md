# Architecture overview

Rune is a local web application. Next.js owns presentation and browser
interactions. FastAPI owns the persistent queue, media, transcription, exports,
and filesystem access.

```text
app/layout.tsx
  -> app/page.tsx
    -> TranscriptionWorkspace client boundary
      -> SourceComposer
      -> JobQueue

app/transcriptions/[job-id]/page.tsx
  -> TranscriptWorkspace client boundary
    -> MediaPlayer
    -> TranscriptDocument
    -> ExportPanel
```

Pages and layouts remain Server Components. Interactive client boundaries call
functional services under `lib/services/`. The frontend never imports Python,
executes media commands, reads arbitrary paths, or owns durable job truth.

The local API URL comes from `NEXT_PUBLIC_RUNE_API_URL` and defaults to the
loopback backend. Rune does not use a Next.js BFF.
