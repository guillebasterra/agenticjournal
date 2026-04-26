"""POST /detect — stream cognitive distortion findings for one journal entry.

Wire-format: server-sent events. Each `DistortionFinding` is one SSE frame
(`data: <json>\\n\\n`). The stream ends with an `event: done` frame, or with an
`event: error` frame if the detector raises before any findings are produced.

Request:
  {
    "entry_id": "entry_001",
    "text": "...optional, ignored unless the entry isn't in the graph yet"
  }

If the entry isn't in the graph and `text` is present, the entry is ingested
on-the-fly using the heuristic extractor (no LLM call) so the orchestrator has
*something* to anchor on. This keeps the frontend usable without forcing the
user to call `/ingest` first; an explicit ingest is still recommended for
real-quality graph evidence.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from detector.run import detect, done_event, error_event, finding_to_sse
from graph.extractor import GraphExtractor
from graph.store import default_store
from retrieval.orchestrator import EntryNotIngestedError
from schemas import JournalEntry

log = logging.getLogger(__name__)

router = APIRouter(tags=["detect"])


class DetectRequest(BaseModel):
    entry_id: str
    # Optional: original entry text. Only used to bootstrap the graph if the
    # entry hasn't been ingested yet. Ignored otherwise.
    text: Optional[str] = None
    # Optional: pass-through metadata the bootstrap path needs.
    raw_heading: Optional[str] = None
    date: Optional[str] = None
    source_path: Optional[str] = None


def _bootstrap_entry_if_needed(req: DetectRequest) -> None:
    """If the entry isn't in the graph, ingest it with a heuristic extractor."""
    store = default_store()
    if store.get_entry(req.entry_id) is not None:
        return
    if not req.text:
        raise HTTPException(
            status_code=404,
            detail=(
                f"entry_id={req.entry_id} not found in graph and no `text` "
                f"was provided to bootstrap it. Call POST /ingest first."
            ),
        )
    log.info("auto-ingesting %s (heuristic) before /detect", req.entry_id)
    entry = JournalEntry(
        id=req.entry_id,
        date=req.date,
        raw_heading=req.raw_heading or req.entry_id,
        text=req.text,
        source_path=req.source_path or "<detect-bootstrap>",
    )
    extractor = GraphExtractor(use_llm=False)
    result = extractor.extract(entry)
    store.replace_entry(entry, result.nodes, result.edges)


def _sse_stream(entry_id: str):
    """Generator wrapped by StreamingResponse — turns detect() into SSE bytes."""
    try:
        for finding in detect(entry_id):
            yield finding_to_sse(finding)
    except EntryNotIngestedError as exc:
        yield error_event(str(exc))
        return
    except Exception as exc:  # network failures, model not pulled, etc.
        log.exception("detector failed for %s", entry_id)
        yield error_event(f"detector failed: {exc}")
        return
    yield done_event()


@router.post("/detect")
def detect_route(req: DetectRequest) -> StreamingResponse:
    _bootstrap_entry_if_needed(req)
    return StreamingResponse(
        _sse_stream(req.entry_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
