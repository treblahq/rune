# Performance

1. Keep Server Components as the default.
2. Keep client boundaries focused on real browser interaction.
3. Load only the jobs and transcript data the current screen needs.
4. Reconcile job events by stable job id.
5. Bound polling and stop it when SSE is healthy.
6. Avoid duplicating props or derived queue counts in state.
7. Measure before adding memoization or virtualization.
8. Do not place model, media, or filesystem work in Next.js.

The queue may grow. Render recent active and completed items first, and add
server pagination before attempting client virtualization.
