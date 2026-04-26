"""End-to-end integration test: ingest -> detect on the sample journal.

This is a runnable script, not a pytest module — there is no pytest in the
project's deps and the brief specifies "a small integration test that runs
ingest -> detect ... and prints findings".

Usage:

    cd backend && uv run python -m tests.integration_detect
    # or analyze a single entry:
    cd backend && uv run python -m tests.integration_detect entry_001

Requires a running Ollama with the configured model pulled (default
`deepseek-r1:32b`; override with `OLLAMA_DETECTOR_MODEL`).

Exits non-zero if no findings stream back at all, or if any streamed finding
fails the contract: it must cite at least one global evidence id, and any
personal evidence ids it cites must be entries that exist in the graph.
"""

from __future__ import annotations

import sys
from pathlib import Path

from api.ingest import IngestRequest, run_ingest
from detector.run import detect
from graph.store import default_store
from rag.distortions.seed import SEED_EXAMPLES
from rag.distortions.store import get_collection, rebuild_collection
from schemas import DistortionFinding

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_journal.md"


def _ensure_distortions_collection() -> None:
    try:
        get_collection()
    except Exception as exc:
        print(f"[setup] distortions collection unavailable ({exc}); seeding…")
        rebuild_collection(SEED_EXAMPLES)


def _ingest_sample() -> list[str]:
    print(f"[ingest] {SAMPLE_PATH}")
    # Heuristic extractor — fast, no LLM dependency for graph build. The
    # detector still uses the LLM for analysis.
    resp = run_ingest(IngestRequest(path=str(SAMPLE_PATH), use_llm=False))
    print(f"[ingest] {resp.parsed} parsed, {resp.ingested} ingested")
    return [s.id for s in resp.entries]


def _validate_finding(f: DistortionFinding, known_entry_ids: set[str]) -> list[str]:
    problems: list[str] = []
    if not f.evidence_global:
        problems.append("no global evidence cited")
    for eid in f.evidence_personal:
        if eid not in known_entry_ids:
            problems.append(f"personal evidence references unknown entry_id={eid}")
    if not (0.0 <= f.confidence <= 1.0):
        problems.append(f"confidence out of range: {f.confidence}")
    return problems


def _print_finding(idx: int, f: DistortionFinding) -> None:
    print(f"  #{idx} {f.label} ({f.confidence:.2f})")
    print(f"     quote: {f.quote!r}")
    print(f"     rationale: {f.rationale}")
    if f.evidence_global:
        print(f"     evidence_global: {', '.join(f.evidence_global)}")
    if f.evidence_personal:
        print(f"     evidence_personal: {', '.join(f.evidence_personal)}")


def main(argv: list[str]) -> int:
    _ensure_distortions_collection()
    entry_ids = _ingest_sample()
    if not entry_ids:
        print("[fail] no entries parsed from sample journal", file=sys.stderr)
        return 2

    targets = [argv[1]] if len(argv) > 1 else entry_ids[:1]
    known = set(default_store().all_entry_ids())

    total_findings = 0
    contract_failures: list[str] = []
    for entry_id in targets:
        print(f"\n[detect] {entry_id}")
        try:
            count = 0
            for i, finding in enumerate(detect(entry_id), start=1):
                count += 1
                total_findings += 1
                _print_finding(i, finding)
                problems = _validate_finding(finding, known)
                for p in problems:
                    contract_failures.append(f"{entry_id} #{i}: {p}")
            if count == 0:
                print("  (no findings)")
        except Exception as exc:
            print(f"[fail] detect crashed for {entry_id}: {exc}", file=sys.stderr)
            return 3

    print(f"\n[summary] {total_findings} findings across {len(targets)} entries")
    if contract_failures:
        print("[summary] contract failures:", file=sys.stderr)
        for line in contract_failures:
            print(f"  - {line}", file=sys.stderr)
        return 4
    if total_findings == 0:
        print("[fail] zero findings streamed", file=sys.stderr)
        return 5
    print("[ok] integration test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
