"""Markdown journal parser.

The journal is a single .md file where each entry begins with an H3 (`### `)
heading. Headings are messy — examples seen in the wild:

    ### Tuesday, 21 October, 10:55pm
    ###  Wednesday, 22 October, 3:20pm
    ### Thursday, February 6, 2025
    ### Thursday October 24
    ### Classes:
    ###

The parser:
  * uses markdown-it-py to find H3 boundaries (more robust than re.split since
    it ignores `###` inside fenced code blocks),
  * trims and normalises the heading text,
  * tries to extract an ISO date from the heading; year is inferred from
    surrounding entries if the heading is year-less,
  * skips empty entries (heading followed by nothing).

Entry ids are stable: `entry_<NNN>` numbered in document order. This makes
re-ingestion idempotent on the graph store.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from markdown_it import MarkdownIt

from schemas import JournalEntry

_MD = MarkdownIt("commonmark")

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

_WEEKDAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
             "mon", "tue", "tues", "wed", "thu", "thurs", "fri", "sat", "sun"}


def _try_parse_date(heading: str, fallback_year: int | None) -> str | None:
    """Best-effort ISO date from a heading like 'Tuesday, 21 October, 10:55pm'.

    Returns None if no plausible date can be extracted. Year is taken from the
    heading if present; otherwise from `fallback_year` (the most recent year
    seen in the document, or the current year as a last resort).
    """
    h = heading.lower()
    # strip stray punctuation that breaks word boundaries
    h_clean = re.sub(r"[,]", " ", h)

    month = None
    day = None
    year = None

    # explicit year (4 digits)
    m_year = re.search(r"\b(19|20)\d{2}\b", h_clean)
    if m_year:
        year = int(m_year.group(0))

    # find a month name
    for token, mnum in _MONTHS.items():
        if re.search(rf"\b{token}\b", h_clean):
            month = mnum
            break

    # find a day-of-month (1-31), prefer numbers near the month token
    for m in re.finditer(r"\b([0-9]{1,2})(?:st|nd|rd|th)?\b", h_clean):
        n = int(m.group(1))
        if 1 <= n <= 31:
            day = n
            break

    if month is None or day is None:
        return None

    if year is None:
        year = fallback_year if fallback_year is not None else date.today().year

    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def _heading_is_meaningful(heading: str) -> bool:
    """Skip empty headings like '### ' or pure decoration."""
    return bool(heading.strip())


def _split_entries(markdown: str) -> list[tuple[str, str]]:
    """Return a list of (heading_text, body_text) in document order.

    Uses markdown-it-py to find H3 token positions, then slices the raw source
    so we keep the original formatting (lists, paragraph breaks, etc.) inside
    each entry.
    """
    tokens = _MD.parse(markdown)
    lines = markdown.splitlines()

    # Collect (heading_text, start_line, end_line_exclusive) for each H3.
    h3_positions: list[tuple[str, int, int]] = []
    open_idx = None
    for i, tok in enumerate(tokens):
        if tok.type == "heading_open" and tok.tag == "h3":
            open_idx = i
        elif tok.type == "heading_close" and tok.tag == "h3" and open_idx is not None:
            inline = tokens[open_idx + 1]
            heading_text = inline.content if inline.type == "inline" else ""
            start_line = tok.map[0] if tok.map else 0  # heading_close shares map
            # heading line itself
            head_line = tokens[open_idx].map[0] if tokens[open_idx].map else 0
            h3_positions.append((heading_text, head_line, head_line))
            open_idx = None

    if not h3_positions:
        return []

    entries: list[tuple[str, str]] = []
    for idx, (heading, head_line, _) in enumerate(h3_positions):
        body_start = head_line + 1
        body_end = h3_positions[idx + 1][1] if idx + 1 < len(h3_positions) else len(lines)
        body = "\n".join(lines[body_start:body_end]).strip()
        entries.append((heading, body))
    return entries


def parse_markdown(markdown: str, source_path: str) -> list[JournalEntry]:
    """Parse a journal markdown string into JournalEntry objects.

    Empty entries (no body) and meaningless headings (e.g. a bare `###`) are
    skipped. Entry ids are assigned in document order over the surviving
    entries: entry_001, entry_002, ...
    """
    pairs = _split_entries(markdown)

    # Walk once to establish a "running year" so year-less headings inherit
    # the most recently seen explicit year.
    last_year: int | None = None
    pending: list[tuple[str, str, str | None]] = []
    for heading, body in pairs:
        if not _heading_is_meaningful(heading) or not body.strip():
            continue
        iso = _try_parse_date(heading, fallback_year=last_year)
        if iso:
            last_year = int(iso[:4])
        pending.append((heading, body, iso))

    entries: list[JournalEntry] = []
    for i, (heading, body, iso) in enumerate(pending, start=1):
        entries.append(
            JournalEntry(
                id=f"entry_{i:03d}",
                date=iso,
                raw_heading=heading.strip(),
                text=body,
                source_path=source_path,
            )
        )
    return entries


def parse_file(path: str | Path) -> list[JournalEntry]:
    p = Path(path)
    return parse_markdown(p.read_text(encoding="utf-8"), source_path=str(p))
