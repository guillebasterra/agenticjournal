"""Read-side queries over the personal graph."""

from __future__ import annotations

import networkx as nx

from schemas import GraphEdge, GraphNeighborhood, GraphNode

from .store import GraphStore, default_store


def neighborhood(
    entry_id: str,
    hops: int = 1,
    store: GraphStore | None = None,
) -> GraphNeighborhood:
    """Subgraph around the entry's anchor node, expanded by `hops` undirected steps.

    The anchor is the synthetic `entry:<entry_id>` node written by the store
    every time an entry is upserted, so this works whether or not the LLM
    extractor produced any other nodes for the entry.
    """
    s = store or default_store()
    g: nx.MultiDiGraph = s.graph
    anchor = f"entry:{entry_id}"

    if anchor not in g:
        return GraphNeighborhood(entry_id=entry_id, nodes=[], edges=[], summary=None)

    # BFS over the underlying undirected view so we follow edges either way.
    undirected = g.to_undirected(as_view=True)
    visited: set[str] = {anchor}
    frontier: set[str] = {anchor}
    for _ in range(max(hops, 0)):
        next_frontier: set[str] = set()
        for node in frontier:
            for nbr in undirected.neighbors(node):
                if nbr not in visited:
                    next_frontier.add(nbr)
        visited.update(next_frontier)
        frontier = next_frontier
        if not frontier:
            break

    nodes: list[GraphNode] = []
    for nid in visited:
        data = g.nodes[nid]
        nodes.append(
            GraphNode(
                id=nid,
                type=data.get("type", "unknown"),
                label=data.get("label", nid),
                attrs=data.get("attrs", {}),
            )
        )

    edges: list[GraphEdge] = []
    seen_edges: set[tuple[str, str, str]] = set()
    for u, v, data in g.edges(data=True):
        if u in visited and v in visited:
            relation = data.get("relation", "related")
            key = (u, v, relation)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append(
                GraphEdge(
                    source=u,
                    target=v,
                    relation=relation,
                    attrs=data.get("attrs", {}),
                )
            )

    entry = s.get_entry(entry_id)
    summary = None
    if entry is not None:
        head = entry.raw_heading or entry_id
        summary = f"{head} ({entry.date or 'no-date'}): {len(nodes)} nodes, {len(edges)} edges within {hops} hops."

    return GraphNeighborhood(
        entry_id=entry_id,
        nodes=nodes,
        edges=edges,
        summary=summary,
    )
