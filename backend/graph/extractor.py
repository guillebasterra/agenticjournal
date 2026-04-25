"""LLM-based entity / event / relation extraction for journal entries.

Uses Ollama's `deepseek-r1:32b` via langchain_ollama. The model is asked to
return a strict JSON document; we parse it into GraphNode and GraphEdge.

Design choices:
  * One LLM call per entry. Entries are short enough (a few paragraphs) that
    we don't need chunking yet.
  * JSON-mode output. We extract the first `{...}` block to be defensive
    against deepseek-r1's habit of leading with a `<think>` reasoning block.
  * Deterministic fallback. If Ollama isn't reachable or returns garbage, we
    still produce a minimal `entry` node + a shallow set of "noun-phrase"
    nodes by lightly tokenising the entry. This keeps `POST /ingest` useful
    in environments without a local Ollama (CI, the global-rag worktree,
    etc.) instead of failing the request outright.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass

from schemas import GraphEdge, GraphNode, JournalEntry

log = logging.getLogger(__name__)

DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "deepseek-r1:32b")
DEFAULT_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

_SYSTEM_PROMPT = """You extract a small knowledge graph from a personal journal entry.

Return STRICT JSON with this exact shape and no commentary:

{
  "nodes": [
    {"id": "entity:<slug>", "type": "entity|event|concept|emotion", "label": "<short>", "attrs": {"category": "person|place|work|object|other"}}
  ],
  "edges": [
    {"source": "<node id or 'entry:THIS_ENTRY'>", "target": "<node id>", "relation": "mentions|describes|feels|involves|about|caused_by|wants|fears|admires", "attrs": {}}
  ]
}

Rules:
- Always include the writer's recurring people, places, and significant objects as nodes.
- Always include the dominant emotions or psychological states as `emotion` nodes.
- Always include any concrete events (something the writer did or that happened) as `event` nodes.
- Use `entry:THIS_ENTRY` (literal string) as the source for top-level edges anchored to the entry itself.
- Node ids must be lowercase, snake_case, prefixed with the type, e.g. `entity:mia`, `event:netflix_interview`, `emotion:overwhelmed`.
- Keep labels short (1-5 words). Do not include the entire sentence.
- Output ONLY the JSON object. Do not wrap it in markdown fences. Do not add explanation.
"""


@dataclass
class ExtractionResult:
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    used_llm: bool


def _slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_") or "x"


def _extract_json_object(text: str) -> dict | None:
    """Find the first balanced JSON object in `text`. Tolerates `<think>` prefixes."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                blob = text[start : i + 1]
                try:
                    return json.loads(blob)
                except json.JSONDecodeError:
                    return None
    return None


def _normalise_extraction(raw: dict, entry_id: str) -> tuple[list[GraphNode], list[GraphEdge]]:
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    seen_node_ids: set[str] = set()

    anchor = f"entry:{entry_id}"

    for n in raw.get("nodes", []) or []:
        if not isinstance(n, dict):
            continue
        nid = n.get("id")
        label = n.get("label")
        ntype = n.get("type", "entity")
        if not isinstance(nid, str) or not isinstance(label, str):
            continue
        if nid == "entry:THIS_ENTRY" or nid == anchor:
            # Anchor node is created by the store; skip duplicates.
            continue
        if nid in seen_node_ids:
            continue
        seen_node_ids.add(nid)
        attrs = n.get("attrs") if isinstance(n.get("attrs"), dict) else {}
        nodes.append(GraphNode(id=nid, type=ntype, label=label, attrs=attrs))

    for e in raw.get("edges", []) or []:
        if not isinstance(e, dict):
            continue
        src = e.get("source")
        tgt = e.get("target")
        rel = e.get("relation", "related")
        if not isinstance(src, str) or not isinstance(tgt, str):
            continue
        # rewrite the placeholder to the real anchor
        if src == "entry:THIS_ENTRY":
            src = anchor
        if tgt == "entry:THIS_ENTRY":
            tgt = anchor
        attrs = e.get("attrs") if isinstance(e.get("attrs"), dict) else {}
        edges.append(GraphEdge(source=src, target=tgt, relation=rel, attrs=attrs))

    return nodes, edges


def _heuristic_fallback(entry: JournalEntry) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Last-resort extraction when the LLM is unavailable.

    Picks out capitalised tokens (likely proper nouns) and a small set of
    emotion words. Crude, but enough that the graph store has *something* to
    return when downstream worktrees query it locally.
    """
    text = entry.text
    anchor = f"entry:{entry.id}"
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    seen: set[str] = set()

    for match in re.finditer(r"\b([A-Z][a-zA-Z]{2,})\b", text):
        word = match.group(1)
        # filter out common sentence-start words
        if word.lower() in {"the", "and", "but", "she", "her", "his", "him", "they",
                            "this", "that", "these", "those", "with", "from", "into",
                            "today", "tomorrow", "yesterday", "monday", "tuesday",
                            "wednesday", "thursday", "friday", "saturday", "sunday",
                            "january", "february", "march", "april", "june", "july",
                            "august", "september", "october", "november", "december"}:
            continue
        nid = f"entity:{_slugify(word)}"
        if nid in seen:
            continue
        seen.add(nid)
        nodes.append(GraphNode(id=nid, type="entity", label=word, attrs={"source": "heuristic"}))
        edges.append(GraphEdge(source=anchor, target=nid, relation="mentions", attrs={}))

    emotions = {
        "overwhelmed": "overwhelmed", "anxious": "anxious", "anxiety": "anxious",
        "stressed": "stressed", "scared": "scared", "happy": "happy", "sad": "sad",
        "angry": "angry", "ashamed": "ashamed", "proud": "proud", "lonely": "lonely",
        "excited": "excited", "depressed": "depressed", "calm": "calm",
        "nauseating": "disgust", "nauseous": "disgust", "liberating": "free",
    }
    lower = text.lower()
    for word, label in emotions.items():
        if re.search(rf"\b{word}\b", lower):
            nid = f"emotion:{label}"
            if nid in seen:
                continue
            seen.add(nid)
            nodes.append(GraphNode(id=nid, type="emotion", label=label, attrs={"source": "heuristic"}))
            edges.append(GraphEdge(source=anchor, target=nid, relation="feels", attrs={}))

    return nodes, edges


class GraphExtractor:
    """Wraps the LangChain Ollama chat model.

    The chat client is constructed lazily so importing this module is cheap and
    doesn't require Ollama to be running.
    """

    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL,
                 use_llm: bool = True):
        self.model = model
        self.base_url = base_url
        self.use_llm = use_llm
        self._chat = None

    def _client(self):
        if self._chat is None:
            from langchain_ollama import ChatOllama  # imported lazily

            self._chat = ChatOllama(
                model=self.model,
                base_url=self.base_url,
                temperature=0,
                format="json",
            )
        return self._chat

    def extract(self, entry: JournalEntry) -> ExtractionResult:
        if not self.use_llm:
            n, e = _heuristic_fallback(entry)
            return ExtractionResult(nodes=n, edges=e, used_llm=False)

        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            chat = self._client()
            messages = [
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"Entry id: {entry.id}\n"
                        f"Date: {entry.date or 'unknown'}\n"
                        f"Heading: {entry.raw_heading}\n"
                        f"Text:\n{entry.text}\n"
                    )
                ),
            ]
            response = chat.invoke(messages)
            content = response.content if hasattr(response, "content") else str(response)
            payload = _extract_json_object(content)
            if payload is None:
                log.warning("extractor: no JSON found for %s; falling back", entry.id)
                n, e = _heuristic_fallback(entry)
                return ExtractionResult(nodes=n, edges=e, used_llm=False)
            nodes, edges = _normalise_extraction(payload, entry.id)
            if not nodes and not edges:
                log.warning("extractor: empty extraction for %s; falling back", entry.id)
                n, e = _heuristic_fallback(entry)
                return ExtractionResult(nodes=n, edges=e, used_llm=False)
            return ExtractionResult(nodes=nodes, edges=edges, used_llm=True)
        except Exception as exc:  # network down, model not pulled, etc.
            log.warning("extractor: LLM call failed for %s (%s); falling back", entry.id, exc)
            n, e = _heuristic_fallback(entry)
            return ExtractionResult(nodes=n, edges=e, used_llm=False)


_DEFAULT: GraphExtractor | None = None


def default_extractor() -> GraphExtractor:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = GraphExtractor()
    return _DEFAULT
