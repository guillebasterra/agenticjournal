# Frontend — Cognitive Debugging

Tauri desktop app. The web layer is **not yet scaffolded** — only an empty `package.json` exists so the workspace start command can install `concurrently`. The first task for the `frontend-shell` worktree is to scaffold Tauri + Vite + a chosen UI framework (React or Svelte — pick one).

## Priorities

1. Scaffold Tauri + Vite + UI framework.
2. **Journal entry view** (load a markdown journal, browse entries, pick an entry).
3. **Distortion result view** that calls `POST /detect` and renders findings with the spans they reference highlighted in the entry.
4. Phase 2: a **persona panel** alongside the distortion view that calls `POST /persona/analyze` and renders persona-grounded analysis. Leave layout space now; do not build it yet.

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

## Current state

- `package.json` exists with `concurrently` as a dev dep so the workspace start command no longer prompts.
- No Vite/React/Svelte/Tauri config yet. No `src/`, no `src-tauri/`.
- The `dev` script is a placeholder that needs replacing during scaffolding.
