"""Shared Pydantic schemas. Every cross-module contract lives here.

If you are adding a field that only one module reads, it does not belong in this
file. If you are adding a field that crosses a worktree boundary, it does.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

DistortionLabel = Literal[
    "catastrophizing",
    "all_or_nothing",
    "emotional_reasoning",
    "mind_reading",
    "fortune_telling",
    "personalization",
    "should_statements",
    "labeling",
    "magnification_minimization",
    "mental_filter",
    "disqualifying_positive",
    "overgeneralization",
]

PersonaName = Literal["marcus_aurelius", "hunter_s_thompson"]


# --- Ingestion / graph ---------------------------------------------------


class JournalEntry(BaseModel):
    id: str
    date: Optional[str] = None  # ISO date if parseable from the heading
    raw_heading: str
    text: str
    source_path: str


class GraphNode(BaseModel):
    id: str
    type: str  # "entity" | "event" | "concept" | ...
    label: str
    attrs: dict = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    attrs: dict = Field(default_factory=dict)


class GraphNeighborhood(BaseModel):
    """Subgraph relevant to a single entry, returned by graph queries."""

    entry_id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    summary: Optional[str] = None


# --- Retrieval -----------------------------------------------------------


class RetrievedDistortionExample(BaseModel):
    id: str
    label: DistortionLabel
    text: str
    explanation: Optional[str] = None
    score: float


class PersonalEvidence(BaseModel):
    entry_id: str
    span: str
    relation: Optional[str] = None


class RetrievalContext(BaseModel):
    """Fused context handed to the detector."""

    entry_id: str
    entry_text: str
    personal: list[PersonalEvidence]
    global_examples: list[RetrievedDistortionExample]


# --- Detection -----------------------------------------------------------


class Span(BaseModel):
    start: int
    end: int


class DistortionFinding(BaseModel):
    label: DistortionLabel
    span: Span
    quote: str
    rationale: str
    evidence_global: list[str]  # ids from the distortions Chroma collection
    evidence_personal: list[str]  # entry ids referenced from the personal graph
    confidence: float


# --- Phase 2: personas ---------------------------------------------------


class RetrievedPersonaPassage(BaseModel):
    persona: PersonaName
    passage_id: str
    text: str
    citation: str  # e.g., "Meditations 4.7" or "Letter to Hume Logan, 1958"
    score: float


class PersonaContext(BaseModel):
    persona: PersonaName
    entry_id: str
    passages: list[RetrievedPersonaPassage]


class PersonaAnalysis(BaseModel):
    persona: PersonaName
    entry_id: str
    analysis: str
    citations: list[str]  # passage_ids referenced in the analysis
