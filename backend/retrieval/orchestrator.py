"""Dual-retrieval orchestrator.

`build_context(entry_id)` fuses two retrievers into the `RetrievalContext` that
the detector consumes:

1. The personal knowledge graph (`graph.query.neighborhood`) — which entities,
   emotions, and events from this entry recur in *other* entries. Recurrence
   across entries is what makes the personal store useful for distortion
   detection: it surfaces the user's own patterns, not just one-off facts.
2. The global Chroma collection of labeled distortion examples
   (`rag.distortions.query.query_distortions`) — semantically similar text
   pulled from CBT-derived seed examples.

The function is intentionally simple and deterministic. Any reasoning happens
downstream in the detector.

Phase 2 will add `persona_passages` to `RetrievalContext`. The shape here is
designed so that addition can be made by setting one new field on the context
object — `personal` and `global_examples` already cover the dimensions the
detector reads today, and the detector should not need to change to ignore an
unset `persona_passages` field.
"""

from __future__ import annotations

import logging

from graph.query import neighborhood
from graph.store import GraphStore, default_store
from rag.distortions.query import query_distortions
from schemas import (
    PersonalEvidence,
    RetrievalContext,
    RetrievedDistortionExample,
)

log = logging.getLogger(__name__)

DEFAULT_HOPS = 1
DEFAULT_K_GLOBAL = 5


class EntryNotIngestedError(LookupError):
    """Raised when build_context is asked for an entry that isn't in the graph."""


def build_context(
    entry_id: str,
    *,
    hops: int = DEFAULT_HOPS,
    k_global: int = DEFAULT_K_GLOBAL,
    store: GraphStore | None = None,
) -> RetrievalContext:
    s = store or default_store()
    entry = s.get_entry(entry_id)
    if entry is None:
        raise EntryNotIngestedError(
            f"entry_id={entry_id!r} not found in graph store; ingest the journal first"
        )

    nh = neighborhood(entry_id, hops=hops, store=s)
    personal = _personal_evidence_from_neighborhood(entry_id, nh, store=s)

    global_examples: list[RetrievedDistortionExample] = []
    try:
        global_examples = query_distortions(entry.text, k=k_global)
    except Exception as exc:  # collection missing, ollama down, etc.
        log.warning(
            "distortions retrieval failed for %s (%s); proceeding with empty global",
            entry_id,
            exc,
        )

    return RetrievalContext(
        entry_id=entry_id,
        entry_text=entry.text,
        personal=personal,
        global_examples=global_examples,
    )


def _personal_evidence_from_neighborhood(
    entry_id: str,
    nh,
    *,
    store: GraphStore,
) -> list[PersonalEvidence]:
    """Project a graph neighborhood into a flat list of PersonalEvidence rows.

    Two kinds of evidence:
      * Direct: edges anchored at this entry (`entry:<id> --rel--> node`). The
        span is the related node's label, the relation is the edge relation.
      * Recurrent: other entries that mention the same non-anchor node. These
        are the patterns worth flagging — the same emotion, event, or person
        showing up across multiple journal days. Span is the shared node's
        label, relation encodes that this is a cross-entry co-occurrence.

    Direct rows always come first so the LLM sees this-entry evidence before
    cross-entry context. Each (entry_id, span, relation) triple is emitted at
    most once.
    """
    anchor = f"entry:{entry_id}"
    nodes_by_id = {n.id: n for n in nh.nodes}

    seen: set[tuple[str, str, str | None]] = set()
    direct: list[PersonalEvidence] = []
    recurrent: list[PersonalEvidence] = []

    for edge in nh.edges:
        if edge.source == anchor and edge.target in nodes_by_id:
            other = nodes_by_id[edge.target]
        elif edge.target == anchor and edge.source in nodes_by_id:
            other = nodes_by_id[edge.source]
        else:
            continue
        if other.id == anchor:
            continue
        key = (entry_id, other.label, edge.relation)
        if key in seen:
            continue
        seen.add(key)
        direct.append(
            PersonalEvidence(
                entry_id=entry_id,
                span=other.label,
                relation=edge.relation,
            )
        )

    g = store.graph
    for node in nh.nodes:
        if node.id == anchor or node.id not in g:
            continue
        node_data = g.nodes[node.id]
        for other_entry in sorted(node_data.get("entry_ids", set())):
            if not other_entry or other_entry == entry_id:
                continue
            relation = f"shares:{node.type}"
            key = (other_entry, node.label, relation)
            if key in seen:
                continue
            seen.add(key)
            recurrent.append(
                PersonalEvidence(
                    entry_id=other_entry,
                    span=node.label,
                    relation=relation,
                )
            )

    return direct + recurrent
