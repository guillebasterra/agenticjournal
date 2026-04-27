# Cognitive Debugging: An Agentic Journal

A Tauri desktop app that analyzes a personal markdown journal, builds a private GraphRAG over it, and surfaces **cognitive distortions** (catastrophizing, all-or-nothing thinking, emotional reasoning, mind-reading, etc.) via dual-retrieval reasoning over both the personal graph and a global ChromaDB of labeled distortion examples. Phase 2 adds **opinionated analysis** through two personas whose public corpora are ingested into the same retrieval system: **Marcus Aurelius** (*Meditations*) and **Hunter S. Thompson** (collected letters, columns, and Gonzo essays).

Frontend stack is **React + Vite + Tauri**. Locked.

## The pipeline

```
Phase 1 — distortion detection:
journal (.md) → ingestion → personal knowledge graph
labeled distortion examples → global ChromaDB
                  │
            dual retrieval
                  │
         local LLM (Ollama)
                  │
        cognitive bias analysis
                  │
                frontend

Phase 2 — opinionated analysis:
persona corpora (two well-known figures) → persona ChromaDB / graph
                  │
       feeds into the same retrieval step
                  │
         local LLM (Ollama)
                  │
       opinionated, persona-grounded analysis
```

Phase 2 plugs into the *existing* retrieval and reasoning code paths. No fork of the pipeline.

## Priorities

1. **Phase 1 — distortion detection.** Build end-to-end, working on real journal input, with results rendered in the frontend. Do not start phase 2 until phase 1 is usable.
2. **Phase 2 — persona-grounded opinionated analysis.** Personas: **Marcus Aurelius** and **Hunter S. Thompson**. Ingest their public corpora and let the same retrieval feed a persona-conditioned analyzer. The voices are intentionally far apart so the contrast is legible.

If a change couples persona logic to detection logic, stop and refactor — they share retrieval, not reasoning.

## Architecture

- **Backend:** Python 3.13 + FastAPI, managed with `uv`. Lives in `backend/`.
- **Frontend:** Tauri (Rust shell + web frontend). Lives in `frontend/`. Currently unscaffolded.
- **LLM:** Ollama running `qwen2.5:7b-instruct` locally by default (chosen for fast first-token + reliable JSON output on Apple-silicon laptops). `deepseek-r1:32b` is supported as a quality-over-speed override via `OLLAMA_DETECTOR_MODEL`. No cloud LLM in the runtime path — privacy is a hard requirement.
- **Knowledge graph:** LangChain + GraphRAG primitives over journal entries.
- **Vector store:** ChromaDB. Two collections — `distortions` (labeled examples) and later `personas` (per-persona corpus chunks).

No formal evaluation harness, no LLM-as-judge, no synthetic-data generation. Iteration is by hand on real journal input.

## Running locally

One-time setup (required before `/detect` will produce real findings):

```bash
ollama pull qwen2.5:7b-instruct                     # ~4.7 GB, default detector model
cd backend && uv run python -m rag.distortions.seed # build the global Chroma collection
```

For higher-quality (but much slower) findings you can swap in a larger reasoning model — e.g. `ollama pull deepseek-r1:32b` and start the backend with `OLLAMA_DETECTOR_MODEL=deepseek-r1:32b`. On a 32B reasoning model expect 30–90 s per entry; on the 7B default expect ~5–10 s.

Then, from the workspace root:

```bash
npx -y concurrently -k -n "backend,frontend" -c "blue,green" \
  "cd backend && uv run uvicorn main:app --reload --port 8000" \
  "cd frontend && npm run tauri dev"
```

The `-y` flag is required so `concurrently` auto-installs without prompting in non-interactive Conductor shells.

## Repo layout

```
backend/      FastAPI app, ingestion, GraphRAG, distortion detector, persona layer
frontend/     Tauri app (to be scaffolded)
.context/     Conductor scratch — notes, schemas, and contracts shared between agents
```

See `backend/CLAUDE.md` and `frontend/CLAUDE.md` for area-specific guidance.

## Worktree plan (Conductor)

Each slice below is one Conductor workspace = one git worktree = one Claude agent. Branch names use `guillebasterra/<slice>`.

**Phase 1 — distortion detection:**

| Worktree | Scope | Touches | Depends on |
|---|---|---|---|
| `ingest-graph` | Markdown parse → entity/event/relation extraction → graph persistence | `backend/ingest/`, `backend/graph/` | — |
| `global-rag` | Curate labeled distortion examples, embed into ChromaDB collection `distortions` | `backend/rag/distortions/` | — |
| `dual-retrieval-detector` | Orchestrator that queries both stores, fuses context, calls Ollama, returns labeled distortions | `backend/retrieval/`, `backend/detector/`, `backend/api/detect.py` | `ingest-graph`, `global-rag` |
| `frontend-shell` | Scaffold Tauri + Vite + chosen UI framework, journal entry view, distortion result view, API client | `frontend/` | — |

`ingest-graph`, `global-rag`, and `frontend-shell` have **zero file overlap** — run all three in parallel today.
`dual-retrieval-detector` blocks on the first two, but its API contract can be agreed up front and frontend work proceeds against a mocked response.

**Phase 2 — persona-grounded analysis:**

| Worktree | Scope | Touches | Depends on |
|---|---|---|---|
| `persona-corpus` | Ingest two persona corpora into ChromaDB collection `personas`, with per-persona namespacing | `backend/rag/personas/` | phase 1 retrieval landed |
| `persona-analyzer` | Persona-conditioned analysis route that reuses dual retrieval and adds persona context | `backend/persona/`, `backend/api/persona.py`, `frontend/` persona panel | `persona-corpus`, `dual-retrieval-detector` |

## Coordination

When a slice produces output another slice consumes, write the Pydantic schema and an example payload to `.context/schemas/` *before* the consumer starts. Concretely, define and commit these early:

- `JournalEntry` (output of `ingest-graph`)
- `RetrievedDistortionExample` (output of `global-rag` queries)
- `RetrievalContext` (input to the detector — fused personal + global hits)
- `DistortionFinding` (output of `/detect`, consumed by frontend)
- Later: `PersonaContext`, `PersonaAnalysis`

## Non-goals

- No cloud LLM in the user runtime path.
- No evaluation framework, no synthetic data, no LLM-as-judge.
- No persona work until distortion detection works on real input end-to-end.
- No mobile, no web deploy — desktop Tauri only.
