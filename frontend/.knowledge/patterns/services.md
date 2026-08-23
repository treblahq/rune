# Service patterns

Frontend services are named functions under `lib/services/`. They use native
`fetch`, accept `AbortSignal`, and map transport failures into enriched native
errors with stable codes.

Services do not import React, own UI copy, retry mutations automatically, or
know the backend framework. Repeated API roots and resource paths use named
constants. Event subscriptions expose an explicit close function and polling is
a separate fallback boundary.
