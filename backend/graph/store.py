"""On-disk personal knowledge graph.

Storage model: a single JSONL file per logical store (default
`backend/data/graph/graph.jsonl`). Each line is one record:

    {"kind": "node", "entry_id": "entry_001", "node": {...GraphNode...}}
    {"kind": "edge", "entry_id": "entry_001", "edge": {...GraphEdge...}}
    {"kind": "entry", "entry_id": "entry_001", "entry": {...JournalEntry...}}

Re-ingesting an entry is idempotent: `replace_entry(entry_id, ...)` rewrites
the file with the old records for that entry stripped out, then appends the
new ones. This is fine at journal scale (low thousands of entries) and keeps
the on-disk format trivially diffable.

We keep an in-memory `networkx.MultiDiGraph` for queries; it is rebuilt from
the JSONL on first access.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Iterable

import networkx as nx

from schemas import GraphEdge, GraphNode, JournalEntry

DEFAULT_GRAPH_PATH = Path(__file__).resolve().parent.parent / "data" / "graph" / "graph.jsonl"


class GraphStore:
    """Thread-safe append/replace store backed by JSONL + an in-memory MultiDiGraph."""

    def __init__(self, path: str | Path = DEFAULT_GRAPH_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()
        self._lock = threading.Lock()
        self._graph: nx.MultiDiGraph | None = None
        self._entries: dict[str, JournalEntry] = {}

    # ---------- public read API ----------

    @property
    def graph(self) -> nx.MultiDiGraph:
        if self._graph is None:
            self._load()
        assert self._graph is not None
        return self._graph

    def get_entry(self, entry_id: str) -> JournalEntry | None:
        if self._graph is None:
            self._load()
        return self._entries.get(entry_id)

    def all_entry_ids(self) -> list[str]:
        if self._graph is None:
            self._load()
        return list(self._entries.keys())

    # ---------- public write API ----------

    def replace_entry(
        self,
        entry: JournalEntry,
        nodes: Iterable[GraphNode],
        edges: Iterable[GraphEdge],
    ) -> None:
        """Idempotent upsert of one entry's records."""
        nodes = list(nodes)
        edges = list(edges)
        with self._lock:
            self._rewrite_without(entry.id)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"kind": "entry", "entry_id": entry.id, "entry": entry.model_dump()}) + "\n")
                # Always include an "entry" node so graph queries can anchor on it.
                entry_node = GraphNode(
                    id=f"entry:{entry.id}",
                    type="entry",
                    label=entry.raw_heading or entry.id,
                    attrs={
                        "date": entry.date,
                        "source_path": entry.source_path,
                    },
                )
                f.write(json.dumps({"kind": "node", "entry_id": entry.id, "node": entry_node.model_dump()}) + "\n")
                for n in nodes:
                    f.write(json.dumps({"kind": "node", "entry_id": entry.id, "node": n.model_dump()}) + "\n")
                for e in edges:
                    f.write(json.dumps({"kind": "edge", "entry_id": entry.id, "edge": e.model_dump()}) + "\n")
            # invalidate; lazy reload on next read
            self._graph = None
            self._entries = {}

    # ---------- internals ----------

    def _rewrite_without(self, entry_id: str) -> None:
        if not self.path.exists():
            return
        kept: list[str] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("entry_id") == entry_id:
                    continue
                kept.append(line)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            for line in kept:
                f.write(line + "\n")
        tmp.replace(self.path)

    def _load(self) -> None:
        g = nx.MultiDiGraph()
        entries: dict[str, JournalEntry] = {}
        node_origins: dict[str, set[str]] = {}
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    kind = rec.get("kind")
                    eid = rec.get("entry_id")
                    if kind == "entry":
                        entries[eid] = JournalEntry(**rec["entry"])
                    elif kind == "node":
                        nd = rec["node"]
                        node_id = nd["id"]
                        if node_id in g:
                            existing = g.nodes[node_id]
                            existing.setdefault("entry_ids", set()).add(eid)
                        else:
                            g.add_node(
                                node_id,
                                type=nd["type"],
                                label=nd["label"],
                                attrs=nd.get("attrs", {}),
                                entry_ids={eid},
                            )
                        node_origins.setdefault(node_id, set()).add(eid)
                    elif kind == "edge":
                        ed = rec["edge"]
                        g.add_edge(
                            ed["source"],
                            ed["target"],
                            key=f"{ed['relation']}::{eid}",
                            relation=ed["relation"],
                            attrs=ed.get("attrs", {}),
                            entry_id=eid,
                        )
        self._graph = g
        self._entries = entries


_DEFAULT: GraphStore | None = None


def default_store() -> GraphStore:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = GraphStore()
    return _DEFAULT
