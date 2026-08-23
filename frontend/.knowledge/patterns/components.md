# Component patterns

Keep component APIs small and behavior-oriented. Pass domain data and actions,
not transport responses. Route-private compositions stay in `_components/`.
Promote them only after another route needs the complete contract.

One component folder contains its `index.tsx`, optional `types.ts`, and owned
microcomponents. Do not reach into another component's private children.
