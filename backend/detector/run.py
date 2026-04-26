"""Streaming distortion detector.

`detect(entry_id)` builds the dual-retrieval context, calls Ollama with the
prompts in this module's sibling, and yields `DistortionFinding` objects as
soon as they are parseable from the model's streamed output.

Streaming model:
  * The system prompt asks the model to wrap its findings in
    `<FINDINGS>...</FINDINGS>` sentinels (see `prompts.py`).
  * `_iter_finding_blobs` watches the byte stream for the open sentinel, then
    runs a brace-balanced scanner over what follows, yielding each top-level
    JSON object string as it becomes complete.
  * Findings are validated with `DistortionFinding.model_validate_json`.
    Anything that doesn't validate is logged and skipped — we don't want a
    single malformed object to abort an otherwise-useful stream.

The detector is intentionally tolerant of `<think>...</think>` reasoning
prefixes that deepseek-r1 emits: the sentinel-gated parser ignores everything
before `<FINDINGS>`.
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Iterable, Iterator

from pydantic import ValidationError

from graph.store import GraphStore
from retrieval.orchestrator import build_context
from schemas import DistortionFinding, RetrievalContext

from .prompts import FINDINGS_CLOSE, FINDINGS_OPEN, build_messages

log = logging.getLogger(__name__)

DEFAULT_MODEL = os.environ.get("OLLAMA_DETECTOR_MODEL", os.environ.get("OLLAMA_MODEL", "deepseek-r1:32b"))
DEFAULT_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


def detect(
    entry_id: str,
    *,
    store: GraphStore | None = None,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
) -> Iterator[DistortionFinding]:
    """Stream `DistortionFinding` for one ingested journal entry.

    Order of operations:
      1. Build the dual-retrieval context (raises if the entry isn't in the
         graph).
      2. Open a streaming chat call to Ollama.
      3. Parse findings out of the model's output as they complete.
    """
    ctx = build_context(entry_id, store=store)
    yield from detect_from_context(ctx, model=model, base_url=base_url)


def detect_from_context(
    ctx: RetrievalContext,
    *,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
) -> Iterator[DistortionFinding]:
    """Same as `detect`, but skips the graph lookup. Useful for tests."""
    chunks = _ollama_chat_stream(ctx, model=model, base_url=base_url)
    for blob in _iter_finding_blobs(chunks):
        finding = _parse_finding(blob)
        if finding is not None:
            yield finding


def _parse_finding(blob: str) -> DistortionFinding | None:
    """Validate one JSON blob into a DistortionFinding.

    Normalises a few shape quirks observed from local models (omitted lists,
    `confidence` clamped outside [0,1]) and enforces the contract documented
    in the system prompt: every finding MUST cite at least one global
    evidence id. Findings that don't are dropped rather than streamed —
    ungrounded findings are exactly what dual-retrieval is meant to prevent.
    """
    try:
        raw = json.loads(blob)
    except json.JSONDecodeError as exc:
        log.warning("dropping unparseable JSON blob: %s\n  blob=%s", exc, blob[:200])
        return None
    if not isinstance(raw, dict):
        return None
    raw.setdefault("evidence_global", [])
    raw.setdefault("evidence_personal", [])
    if isinstance(raw.get("confidence"), (int, float)):
        raw["confidence"] = max(0.0, min(1.0, float(raw["confidence"])))
    try:
        finding = DistortionFinding.model_validate(raw)
    except ValidationError as exc:
        log.warning("dropping malformed finding: %s\n  blob=%s", exc, blob[:200])
        return None
    if not finding.evidence_global:
        log.info("dropping ungrounded finding (no evidence_global): %s", finding.label)
        return None
    return finding


def _ollama_chat_stream(
    ctx: RetrievalContext,
    *,
    model: str,
    base_url: str,
) -> Iterator[str]:
    """Stream raw text chunks from an Ollama chat call.

    Imported lazily so importing this module does not require ollama on disk
    or a running daemon (handy for tests of the parser alone).
    """
    import ollama

    client = ollama.Client(host=base_url)
    messages = build_messages(ctx)
    stream = client.chat(model=model, messages=messages, stream=True)
    for part in stream:
        # ollama-python yields ChatResponse-like dicts: {"message": {"content": "..."}}
        msg = part.get("message") if isinstance(part, dict) else getattr(part, "message", None)
        if msg is None:
            continue
        content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
        if content:
            yield content


# ---------------- streaming JSON extraction ----------------------------------


def _iter_finding_blobs(chunks: Iterable[str]) -> Iterator[str]:
    """Yield raw JSON-object source strings from a streamed text source.

    Looks for `<FINDINGS>` to start, ignores everything before it. Inside, it
    runs a brace-balanced scanner (string- and escape-aware) over the buffer
    and yields each complete top-level object. Stops at `</FINDINGS>`.

    `cursor` persists across chunks so brace counts don't get double-counted
    when an object spans a chunk boundary.
    """
    buffer = ""
    started = False
    cursor = 0
    obj_start = -1
    depth = 0
    in_str = False
    esc = False

    for chunk in chunks:
        if not chunk:
            continue
        buffer += chunk

        if not started:
            idx = buffer.find(FINDINGS_OPEN)
            if idx == -1:
                # Keep enough tail in case the sentinel straddles chunks.
                if len(buffer) > len(FINDINGS_OPEN):
                    buffer = buffer[-len(FINDINGS_OPEN) :]
                continue
            started = True
            buffer = buffer[idx + len(FINDINGS_OPEN) :]
            cursor = 0
            obj_start = -1

        while cursor < len(buffer):
            ch = buffer[cursor]
            if obj_start == -1:
                if ch == "{":
                    obj_start = cursor
                    depth = 1
                    in_str = False
                    esc = False
                    cursor += 1
                    continue
                if buffer.startswith(FINDINGS_CLOSE, cursor):
                    return
                cursor += 1
                continue

            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    blob = buffer[obj_start : cursor + 1]
                    yield blob
                    buffer = buffer[cursor + 1 :]
                    obj_start = -1
                    cursor = 0
                    continue
            cursor += 1


# ---------------- light helpers used by the integration test -----------------


def detect_to_list(entry_id: str, **kwargs) -> list[DistortionFinding]:
    """Eagerly collect findings into a list. Useful in tests."""
    return list(detect(entry_id, **kwargs))


def finding_to_sse(finding: DistortionFinding) -> bytes:
    """Encode one finding as an SSE `data:` frame."""
    payload = finding.model_dump_json()
    return f"data: {payload}\n\n".encode("utf-8")


def done_event() -> bytes:
    return b"event: done\ndata: {}\n\n"


def error_event(message: str) -> bytes:
    payload = json.dumps({"error": message})
    return f"event: error\ndata: {payload}\n\n".encode("utf-8")
