"""POST /ingest — parse a journal markdown blob or path, populate the graph."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from graph.extractor import GraphExtractor, default_extractor
from graph.store import GraphStore, default_store
from ingest.parser import parse_file, parse_markdown
from schemas import JournalEntry

log = logging.getLogger(__name__)

router = APIRouter(tags=["ingest"])


class IngestRequest(BaseModel):
    # Exactly one of `markdown` or `path` should be provided.
    markdown: Optional[str] = None
    path: Optional[str] = None
    # Skip the LLM call (useful in CI / tests). When false (default), we still
    # fall back to a heuristic if Ollama isn't reachable — this flag forces it.
    use_llm: bool = True


class IngestEntrySummary(BaseModel):
    id: str
    date: Optional[str]
    raw_heading: str
    nodes: int
    edges: int
    used_llm: bool


class IngestResponse(BaseModel):
    source_path: str
    parsed: int
    ingested: int
    entries: list[IngestEntrySummary]


def _resolve_source(req: IngestRequest) -> tuple[list[JournalEntry], str]:
    if req.path and req.markdown:
        raise HTTPException(400, "provide exactly one of `markdown` or `path`")
    if req.path:
        p = Path(req.path)
        if not p.is_absolute():
            # Resolve relative to the backend root so callers can say `data/journal.md`.
            p = Path(__file__).resolve().parent.parent / p
        if not p.exists():
            raise HTTPException(404, f"journal not found at {p}")
        return parse_file(p), str(p)
    if req.markdown:
        return parse_markdown(req.markdown, source_path="<inline>"), "<inline>"
    # default: ingest the project's sample journal
    sample = Path(__file__).resolve().parent.parent / "data" / "sample_journal.md"
    if not sample.exists():
        raise HTTPException(400, "no `markdown` or `path` provided and no sample_journal.md present")
    return parse_file(sample), str(sample)


def run_ingest(
    req: IngestRequest,
    store: GraphStore | None = None,
    extractor: GraphExtractor | None = None,
) -> IngestResponse:
    """Pure ingest function — used by the route and by tests/scripts."""
    s = store or default_store()
    ex = extractor or (GraphExtractor(use_llm=False) if not req.use_llm else default_extractor())

    entries, source_path = _resolve_source(req)
    summaries: list[IngestEntrySummary] = []
    for entry in entries:
        try:
            result = ex.extract(entry)
        except Exception as exc:
            log.exception("extraction crashed for %s", entry.id)
            raise HTTPException(500, f"extraction failed for {entry.id}: {exc}")
        s.replace_entry(entry, result.nodes, result.edges)
        summaries.append(
            IngestEntrySummary(
                id=entry.id,
                date=entry.date,
                raw_heading=entry.raw_heading,
                nodes=len(result.nodes),
                edges=len(result.edges),
                used_llm=result.used_llm,
            )
        )

    return IngestResponse(
        source_path=source_path,
        parsed=len(entries),
        ingested=len(summaries),
        entries=summaries,
    )


@router.post("/ingest", response_model=IngestResponse)
def ingest_route(req: IngestRequest | None = None) -> IngestResponse:
    return run_ingest(req or IngestRequest())
