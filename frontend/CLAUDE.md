# Frontend — Cognitive Debugging

Tauri 2 desktop app. **Stack: Tauri 2 + Vite + React + TypeScript + Tailwind.** Locked.

## Priorities

1. **Journal entry view** — load a markdown journal via Tauri fs/dialog, parse `### heading` boundaries, browse entries, pick one.
2. **Distortion result view** — call `POST /detect` (SSE-streamed) and render `DistortionFinding[]` with `span` ranges highlighted inline in the entry text.
3. Phase 2: **persona panel** alongside the distortion view that calls `POST /persona/analyze`. Layout slot is reserved (`PersonaPanelPlaceholder`); do not build the contents until phase 1 is usable end-to-end.

## Backend contract

The backend runs at `http://localhost:8000`. Always go through a single API client module so the host can later be swapped for a Tauri command if the backend moves in-process.

Phase-1 endpoints (see `backend/CLAUDE.md` for full shape):

- `POST /ingest` — load/refresh the personal graph from a markdown journal.
- `POST /detect` — analyze an entry, return distortion findings with evidence from both retrievals.

Phase-2 endpoints:

- `POST /persona/ingest`
- `POST /persona/analyze`

## Conventions

- **No cloud calls from the frontend.** All LLM access goes through the local backend. Privacy is project-level non-negotiable.
- **Don't ship UI for fields the backend doesn't return.** If `/detect` doesn't include a field, don't render it.
- **Decouple editor from analyzer.** The journal editor should not know how distortions are detected, and the analyzer view should not know how the editor stores text. They communicate via entry id + the API.
- **Stream where the backend streams.** The detector route streams; render findings progressively rather than waiting for the full response.

## Running

From the workspace root:

```bash
npx -y concurrently -k -n "backend,frontend" -c "blue,green" \
  "cd backend && uv run uvicorn main:app --reload --port 8000" \
  "cd frontend && npm run tauri dev"
```

`npm run tauri dev` will fail until the Tauri scaffold lands — that's expected and is the first task.

## Layout

```
frontend/
  index.html
  vite.config.ts
  tailwind.config.js  postcss.config.js  tsconfig.json
  package.json        package-lock.json
  src/
    main.tsx          App.tsx          index.css
    api/
      client.ts       # ingest, detectStream (SSE), mock dev mode
      types.ts        # mirror of backend/schemas.py
    lib/
      parseJournal.ts # `### heading` → JournalEntry[]
      loadJournal.ts  # bundled sample + Tauri fs/dialog picker
    views/
      JournalView.tsx # entry list + journal source picker
      DetectView.tsx  # /detect call + highlighted text + findings sidebar
    components/
      EntryList.tsx   HighlightedEntry.tsx   PersonaPanelPlaceholder.tsx
    fixtures/
      sample_journal.md   mock_findings.json
  src-tauri/
    Cargo.toml  build.rs  tauri.conf.json
    src/main.rs  src/lib.rs
    capabilities/default.json   icons/...
```

## Dev modes

- `npm run dev` — Vite only (browser at http://localhost:1420). Useful for fast UI iteration; Tauri-only APIs (fs, dialog) error.
- `npm run tauri dev` — full desktop app. The Rust shell auto-runs `npm run dev` as `beforeDevCommand`.
- `VITE_USE_MOCK_DETECT=1 npm run tauri dev` — `/detect` is replayed from `src/fixtures/mock_findings.json`. Use this when the backend isn't running yet.
- `VITE_API_BASE_URL=http://localhost:8000` — override the backend host (default is `http://localhost:8000`).

## API client

Single module: `src/api/client.ts`. All HTTP from the renderer goes through it. `detectStream` consumes SSE — one `data:` frame = one `DistortionFinding` (mirroring `backend/schemas.py::DistortionFinding`). `event: done` (or stream close) ends the stream.

## Cross-worktree contract

Schema mirrors live in `.context/schemas/`:

- `journal_entry.json` — produced by `ingest-graph`, consumed here.
- `distortion_finding.json` — produced by `dual-retrieval-detector`, consumed here.

When either schema changes upstream, update both `src/api/types.ts` and the relevant fixture.
