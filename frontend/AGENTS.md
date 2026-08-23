<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

# Rune frontend instructions

`AGENTS.md` is the canonical instruction file for the Rune Next.js interface.
`CLAUDE.md` delegates to it. Topic-specific guidance lives in `.knowledge/`.

## Product and stack

Rune turns local or linked audio and video into text without sending media to a
hosted service.

- Next.js 16.3 App Router
- React 19 and strict TypeScript
- Tailwind CSS 4
- npm and Node 24
- Vitest, Testing Library, and Playwright
- Local FastAPI service at the configured loopback URL

The primary UI is Brazilian Portuguese. Code, identifiers, comments, technical
documentation, and commits are English.

## Routes

```text
app/
├── layout.tsx
├── page.tsx                              # Composer and persistent queue
└── transcriptions/[job-id]/
    ├── page.tsx                          # Result route
    └── _components/                      # Result-private interactive UI
components/                               # App-wide reusable components
lib/
├── enums/                                # Closed domain states
├── helpers/                              # Pure transformations
├── services/                             # FastAPI transport
└── types/                                # Shared domain and transport types
```

## Server and client boundaries

- Keep pages and layouts as Server Components unless browser APIs, events, or
  React client state require a Client Component.
- Add `"use client"` at the smallest practical interactive boundary.
- The composer, live queue, media player, and editable transcript are focused
  client boundaries.
- Do not proxy the loopback API through Next.js Route Handlers.
- Never put filesystem paths, model logic, or media processing in the frontend.

## Components

- Every ordinary component lives in a kebab-case folder with `index.tsx`.
- Component props live in `types.ts` when props exist.
- Component-private children live directly inside the owning component folder.
- Route-private components live in the route segment's `_components/` folder.
- Shared components live under `components/` only after real reuse.
- Do not create Atomic Design folders or barrel-only `index.ts` files.
- Use semantic HTML and native controls before ARIA.
- Declare `React.ReactNode` as the return type of every React component.

## Styling and brand

- Use Tailwind utilities directly in JSX.
- `app/globals.css` owns the Tailwind import, theme aliases, document defaults,
  class-controlled dark variant, focus treatment, selection, and reduced-motion
  safety only.
- Do not add CSS Modules, CSS-in-JS, authored component selectors, glass effects,
  loud gradients, or generic AI-purple decoration.
- Use warm paper and white surfaces in Light, near-black and graphite surfaces
  in Dark, dark green ink, and mint for bounded primary actions and selection.
- Keep semantic success, warning, and danger independent from the brand mint.
- Use Figtree for product copy and Geist Mono for technical data.
- Preserve the approved monochrome Rune mark. Do not distort, recolor internal
  pieces, or place it on an arbitrary decorative tile.
- Support 320, 375, 768, 1024, 1280, and 1440 CSS pixel widths.

## State and data

- Use local state for one interactive subtree.
- Lift state only to the closest shared owner.
- The main workspace owns the current jobs collection and event subscription.
- The URL owns the selected transcript through `/transcriptions/[job-id]`.
- The FastAPI service and SQLite database own durable queue and transcript state.
- Do not add Redux, Zustand, a query client, or browser persistence for the
  current scope.
- Derive values during render instead of mirroring them in state.
- Use effects only to synchronize with uploads, events, timers, media, or other
  external systems. Keep exhaustive dependencies.

## Services and errors

- Services are named functions under `lib/services/`; they do not import React.
- Use the configured `@/*` alias across ownership boundaries and relative imports
  within one component or feature.
- Model closed domain states with string enums in `lib/enums/`.
- Enrich native `Error` objects through factories instead of custom classes.
- Components consume safe error codes and messages; they never display backend
  logs, exception names, or raw filesystem paths.
- Use Server-Sent Events for live updates and bounded polling as a fallback.

## Copy

- Keep copy calm, direct, and specific.
- Do not use hype, artificial urgency, AI jargon, fake insight, or vague claims.
- Say what happened and what the user can safely do next.
- Confirm that original files remain untouched when a processing error occurs.
- Primary promise: `Seu áudio, em texto. Sem sair do seu Mac.`
- Primary action: `Adicionar à fila`.

## Testing and validation

Use TDD for behavior changes.

Run from `frontend/`:

```bash
npm run test
npm run lint
npm run typecheck
npm run build
```

`npm run check` runs the complete frontend gate. Interactive changes also need
desktop, mobile, keyboard, and reduced-motion verification.

## Knowledge base

- [Index](.knowledge/README.md)
- [Architecture](.knowledge/architecture/overview.md)
- [State management](.knowledge/architecture/state-management.md)
- [Design system](.knowledge/design_system/README.md)
- [Styling](.knowledge/best-practices/styling.md)
- [Components](.knowledge/patterns/components.md)
- [Services](.knowledge/patterns/services.md)
