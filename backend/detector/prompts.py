"""Prompt construction for the cognitive distortion detector.

The model is asked to read one journal entry, plus two retrievals (recurring
patterns from the personal graph and labeled examples from the global Chroma
store), and emit a stream of `DistortionFinding` JSON objects between sentinel
markers. Sentinels make stream parsing robust against `<think>` reasoning
blocks and to any commentary the model might leak around the JSON.

Output contract (mirrors `schemas.DistortionFinding`):

    {
      "label": "<one of the allowed labels>",
      "span": {"start": <int>, "end": <int>},  // char offsets into entry_text
      "quote": "<verbatim substring of entry_text>",
      "rationale": "<one or two sentences>",
      "evidence_global": ["<distortion example id>", ...],
      "evidence_personal": ["<entry id>", ...],
      "confidence": <float in [0, 1]>
    }
"""

from __future__ import annotations

from typing import get_args

from schemas import DistortionLabel, RetrievalContext

ALLOWED_LABELS: tuple[str, ...] = tuple(get_args(DistortionLabel))

FINDINGS_OPEN = "<FINDINGS>"
FINDINGS_CLOSE = "</FINDINGS>"


SYSTEM_PROMPT = f"""You are a careful cognitive-behavioral therapist reviewing a single
journal entry for cognitive distortions (Burns / Beck taxonomy).

Your job: identify zero or more concrete distortions in the entry, grounded in
two pieces of retrieved context: (1) labeled distortion examples from a global
clinical reference, and (2) recurring patterns from the user's own past journal
entries. A finding is only worth reporting if it is *visible in the entry text
itself* — do not invent quotes.

Allowed labels (use exactly one per finding):
{", ".join(ALLOWED_LABELS)}

For every finding, return a JSON object with this exact shape and nothing else:

{{
  "label": "<one of the allowed labels>",
  "span": {{"start": <int>, "end": <int>}},
  "quote": "<verbatim substring of entry_text — must equal entry_text[start:end]>",
  "rationale": "<one or two sentences explaining why this is the named distortion>",
  "evidence_global": ["<id from GLOBAL EXAMPLES>", ...],
  "evidence_personal": ["<entry_id from PERSONAL EVIDENCE>", ...],
  "confidence": <float between 0.0 and 1.0>
}}

Rules:
- `quote` MUST be a verbatim substring of the entry text. `start` and `end` are
  character offsets such that `entry_text[start:end] == quote`.
- `evidence_global` MUST be present and contain at least one id from the
  GLOBAL EXAMPLES list. Use the ids exactly as given
  (e.g. "catastrophizing_03"). If no global example applies, omit the finding
  entirely.
- `evidence_personal` MUST be present, even if empty (`[]`). If you cite an
  entry id, it MUST appear in the PERSONAL EVIDENCE block.
- Output the findings as a JSON array placed strictly between the sentinels
  {FINDINGS_OPEN} and {FINDINGS_CLOSE}. No prose outside the array. No
  markdown code fences. If you find nothing, emit an empty array: [].
- You may think privately first; only what appears between the sentinels is
  read by the system.

JSON formatting (this is non-negotiable — malformed JSON is dropped):
- Every string value MUST be enclosed in double quotes.
- Every key MUST be enclosed in double quotes.
- No trailing commas. No comments. No `undefined` or `NaN`.
- Embedded double quotes inside a string MUST be escaped as `\\"`.
- Each finding MUST include all seven keys: label, span, quote, rationale,
  evidence_global, evidence_personal, confidence.

Example of the expected wire format:

{FINDINGS_OPEN}
[
  {{"label": "catastrophizing", "span": {{"start": 12, "end": 64}}, "quote": "...", "rationale": "...", "evidence_global": ["catastrophizing_03"], "evidence_personal": ["entry_002"], "confidence": 0.78}}
]
{FINDINGS_CLOSE}
"""


def _format_personal(ctx: RetrievalContext) -> str:
    if not ctx.personal:
        return "(no recurring patterns in personal history)"
    lines: list[str] = []
    for ev in ctx.personal:
        rel = ev.relation or "related"
        lines.append(f"- entry_id={ev.entry_id} | {rel} | {ev.span}")
    return "\n".join(lines)


def _format_global(ctx: RetrievalContext) -> str:
    if not ctx.global_examples:
        return "(no global examples retrieved)"
    lines: list[str] = []
    for ex in ctx.global_examples:
        explanation = (ex.explanation or "").strip()
        suffix = f"  // {explanation}" if explanation else ""
        lines.append(
            f"- id={ex.id} | label={ex.label} | score={ex.score:.2f}\n"
            f"    text: {ex.text}{suffix}"
        )
    return "\n".join(lines)


def build_user_prompt(ctx: RetrievalContext) -> str:
    """Render the per-call user message with context blocks."""
    return (
        f"ENTRY (id={ctx.entry_id}, length={len(ctx.entry_text)} chars):\n"
        f"```\n{ctx.entry_text}\n```\n\n"
        f"PERSONAL EVIDENCE (entries from this user's history that share "
        f"entities/emotions/events with the current entry):\n"
        f"{_format_personal(ctx)}\n\n"
        f"GLOBAL EXAMPLES (semantically similar labeled distortions from the "
        f"clinical reference):\n"
        f"{_format_global(ctx)}\n\n"
        f"Now identify the cognitive distortions present in the ENTRY. Cite at "
        f"least one global id per finding. Emit the JSON array between "
        f"{FINDINGS_OPEN} and {FINDINGS_CLOSE}."
    )


def build_messages(ctx: RetrievalContext) -> list[dict]:
    """Return Ollama-style chat messages for the detector call."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(ctx)},
    ]
