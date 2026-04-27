# Backend — Cognitive Debugging

Python 3.13, managed with `uv`. FastAPI + uvicorn. Hosts the ingestion pipeline, the personal knowledge graph, ChromaDB-backed retrieval, the distortion detector, and (phase 2) the persona-grounded analyzer.

The runtime LLM is **local Ollama**. The default detector model is `qwen2.5:7b-instruct` (~4.7 GB, ~5–10 s per entry on Apple-silicon laptops, reliable JSON output). `deepseek-r1:32b` is supported as a quality-over-speed override via `OLLAMA_DETECTOR_MODEL` but is much slower because of its reasoning prefix. There is no cloud LLM anywhere in this backend, period. No evaluation harness, no LLM-as-judge, no synthetic data tooling.

## Priorities

1. End-to-end **distortion detection** on real journal input: ingest → graph → dual retrieval → local-model analysis → labeled findings returned over HTTP.
2. **Persona layer** that ingests two persona corpora and produces persona-grounded analysis using the same retrieval path. Build only after (1) is working in the frontend.

If a PR adds a layer that doesn't move (1) toward done, it's premature.

## Layout (target — most directories don't exist yet)

```
backend/
  main.py                  FastAPI app entrypoint (uvicorn target)
  pyproject.toml           uv-managed deps
  schemas.py               Pydantic models shared across modules
  data/                    raw + processed journal data (gitignored except samples)
  ingest/                  markdown → structured entries → graph triples
  graph/                   GraphRAG construction, persistence, queries
  rag/
    distortions/           ChromaDB collection of labeled distortion examples
    personas/              [phase 2] ChromaDB collection per persona
  retrieval/               dual-retrieval orchestrator (graph + distortions, + personas in p2)
  detector/                distortion classifier built on retrieval context, calling Ollama
  persona/                 [phase 2] persona-conditioned analyzer
  api/                     FastAPI routers (ingest, detect, persona, ...)
```

When you create a new module, update this map.

## Setup / running

```bash
cd backend
uv sync
ollama pull qwen2.5:7b-instruct              # default detector model
uv run python -m rag.distortions.seed        # builds the `distortions` Chroma collection
uv run uvicorn main:app --reload --port 8000
```

Ollama must be running with the configured model pulled before the detector or persona analyzer paths will work; if the model is missing the SSE stream emits an `event: error` frame with the Ollama 404 message. To swap models, set `OLLAMA_DETECTOR_MODEL` before starting uvicorn (e.g. `OLLAMA_DETECTOR_MODEL=deepseek-r1:32b` for higher-quality but much slower output, or `OLLAMA_DETECTOR_MODEL=llama3.1:8b`). Models smaller than ~7B (e.g. `llama3.2:3b`) tend to produce malformed JSON for this prompt and have all findings dropped — avoid them.

The `distortions` Chroma collection is also a prereq — without it the orchestrator logs `Collection [distortions] does not exist` and proceeds with empty global evidence (findings will be poorly grounded). Re-run the seed command whenever `rag/distortions/seed.py` changes. Ingestion and ChromaDB population themselves can run without Ollama.

## Conventions

- **Dependencies:** add via `uv add <pkg>`. Don't hand-edit `pyproject.toml` for runtime deps.
- **No cloud LLM SDKs.** Do not add `anthropic`, `openai`, or `google-generativeai` to dependencies. If you find yourself wanting one, you're solving the wrong problem.
- **Schemas first.** When a module's output is another module's input (e.g., `RetrievalContext` feeding the detector), define the Pydantic model in `schemas.py` and drop an example payload in `.context/schemas/` so parallel workstreams can integrate without coordination.
- **Local I/O only.** ChromaDB persists to disk under `backend/data/`. Graph state persists to disk under `backend/data/`. Nothing leaves the machine.
- **Streaming where it helps.** The detector should stream Ollama output to the frontend so analysis appears as it's generated.

## Phase-1 API surface (target)

- `POST /ingest` — accepts a markdown journal (or path), parses it, updates the personal graph. Idempotent on entry id.
- `POST /detect` — accepts a single entry (id or raw text). Returns `List[DistortionFinding]` with `{label, span, evidence_personal, evidence_global, confidence, rationale}`.

Phase 2 adds:

- `POST /persona/ingest` — accepts a persona name and corpus source, builds the persona's Chroma collection.
- `POST /persona/analyze` — accepts an entry id and a persona name, returns persona-grounded analysis using the same retrieval path plus persona context.

## Current state

- `main.py` exposes `/health`, `/ingest`, `/detect`.
- `ingest/` and `graph/` parse a markdown journal into a JSONL-backed `MultiDiGraph`.
- `rag/distortions/` seeds and queries a Chroma collection of labeled CBT examples.
- `retrieval/orchestrator.py::build_context(entry_id)` fuses graph neighborhood + global Chroma hits into a `RetrievalContext`.
- `detector/` calls Ollama (`deepseek-r1:32b` by default; override with `OLLAMA_DETECTOR_MODEL`) and stream-parses sentinel-bracketed JSON findings.
- `api/detect.py` exposes `POST /detect` as SSE — one `data:` frame per `DistortionFinding`, terminated by `event: done`.
- `tests/integration_detect.py` runs `ingest -> detect` end-to-end on `data/sample_journal.md` and prints findings (`uv run python -m tests.integration_detect`).

## What "done" looks like for phase 1

- `POST /detect` returns useful, grounded findings on a real journal entry, citing evidence from both the personal graph and the global distortion store.
- The Tauri frontend renders those findings against the entry text.
- The full pipeline runs offline with only Ollama and local disk.
