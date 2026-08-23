# State management

The FastAPI service and SQLite database own durable jobs and transcripts.

The main workspace owns:

- the current job collection;
- source-composer interaction state;
- Server-Sent Event connection state;
- bounded polling fallback state.

The result workspace owns:

- the loaded transcript draft;
- media playback position;
- active transcript view;
- pending automatic-save state.

Keep state at the lowest owner. Use props for short paths and context only when
multiple distant descendants share one lifecycle. Do not add a global state or
query library. Derive queue counts and labels during render.

The URL is the source of truth for the selected transcript. Durable changes go
through the local API rather than browser storage.
