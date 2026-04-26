import { useCallback, useEffect, useRef, useState } from "react";
import { detectStream, isMockMode } from "../api/client";
import type { DistortionFinding, JournalEntry } from "../api/types";
import { HighlightedEntry } from "../components/HighlightedEntry";

interface Props {
  entry: JournalEntry | null;
}

type Status = "idle" | "loading" | "done" | "error";

export function DetectView({ entry }: Props) {
  const [findings, setFindings] = useState<DistortionFinding[]>([]);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [activeIdx, setActiveIdx] = useState<number | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setFindings([]);
    setStatus("idle");
    setError(null);
    setActiveIdx(null);
  }, []);

  useEffect(() => {
    reset();
  }, [entry?.id, reset]);

  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  const handleDetect = useCallback(async () => {
    if (!entry) return;
    abortRef.current?.abort();
    const ctl = new AbortController();
    abortRef.current = ctl;
    setFindings([]);
    setStatus("loading");
    setError(null);
    setActiveIdx(null);

    try {
      await detectStream(
        { entry_id: entry.id, text: entry.text },
        {
          signal: ctl.signal,
          onFinding: (f) => setFindings((prev) => [...prev, f]),
          onError: (err) => {
            setError(err.message);
            setStatus("error");
          },
          onDone: () =>
            setStatus((s) => (s === "error" ? s : "done")),
        },
      );
    } catch (err) {
      if (ctl.signal.aborted) return;
      setError(err instanceof Error ? err.message : String(err));
      setStatus("error");
    }
  }, [entry]);

  if (!entry) {
    return (
      <main className="flex-1 flex items-center justify-center text-mute italic">
        Select an entry to begin.
      </main>
    );
  }

  return (
    <main className="flex-1 flex flex-col overflow-hidden">
      <div className="px-6 py-4 border-b border-stone-200 flex items-baseline gap-3">
        <div className="flex-1 min-w-0">
          <div className="text-xs uppercase tracking-wide text-mute">
            {entry.date ?? "Undated"}
          </div>
          <h1 className="text-xl font-semibold truncate">{entry.raw_heading}</h1>
        </div>
        <button
          type="button"
          onClick={handleDetect}
          disabled={status === "loading"}
          className="text-sm px-3 py-1.5 bg-ink text-paper rounded hover:bg-stone-700 disabled:opacity-50"
        >
          {status === "loading" ? "Detecting…" : "Detect distortions"}
        </button>
        {isMockMode() && (
          <span
            className="text-[10px] uppercase tracking-wider px-2 py-0.5 bg-yellow-100 border border-yellow-300 rounded"
            title="VITE_USE_MOCK_DETECT=1 — /detect is mocked from frontend fixture"
          >
            mock
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto grid grid-cols-1 lg:grid-cols-[3fr_2fr] gap-0">
        <section className="p-6 border-r border-stone-200">
          <HighlightedEntry
            text={entry.text}
            findings={findings}
            activeIndex={activeIdx}
            onHover={setActiveIdx}
          />
        </section>
        <section className="p-6 bg-stone-50">
          <FindingsList
            findings={findings}
            activeIndex={activeIdx}
            onHover={setActiveIdx}
            status={status}
            error={error}
          />
        </section>
      </div>
    </main>
  );
}

interface FindingsListProps {
  findings: DistortionFinding[];
  activeIndex: number | null;
  onHover: (idx: number | null) => void;
  status: Status;
  error: string | null;
}

function FindingsList({
  findings,
  activeIndex,
  onHover,
  status,
  error,
}: FindingsListProps) {
  return (
    <div className="space-y-3">
      <div className="text-xs uppercase tracking-wide text-mute mb-2">
        Findings {findings.length > 0 && `(${findings.length})`}
      </div>

      {status === "idle" && findings.length === 0 && (
        <div className="text-sm text-mute italic">
          Click <span className="font-medium">Detect distortions</span> to analyze this entry.
        </div>
      )}

      {status === "loading" && findings.length === 0 && (
        <div className="text-sm text-mute italic">Streaming findings…</div>
      )}

      {status === "error" && error && (
        <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded p-3">
          {error}
        </div>
      )}

      {findings.map((f, idx) => (
        <FindingCard
          key={idx}
          finding={f}
          active={idx === activeIndex}
          onMouseEnter={() => onHover(idx)}
          onMouseLeave={() => onHover(null)}
        />
      ))}

      {status === "done" && findings.length === 0 && (
        <div className="text-sm text-mute italic">
          No distortions detected in this entry.
        </div>
      )}
    </div>
  );
}

interface FindingCardProps {
  finding: DistortionFinding;
  active: boolean;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}

function FindingCard({ finding, active, onMouseEnter, onMouseLeave }: FindingCardProps) {
  return (
    <article
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className={`bg-white border rounded p-3 text-sm space-y-2 transition-colors ${
        active ? "border-ink shadow-sm" : "border-stone-200"
      }`}
    >
      <header className="flex items-center justify-between gap-2">
        <span
          className={`dx dx-${finding.label} px-2 py-0.5 rounded text-xs font-medium`}
        >
          {finding.label.replace(/_/g, " ")}
        </span>
        <span className="text-xs font-mono text-mute">
          {(finding.confidence * 100).toFixed(0)}%
        </span>
      </header>
      <blockquote className="border-l-2 border-stone-300 pl-3 italic text-stone-700">
        “{finding.quote}”
      </blockquote>
      <p className="text-stone-700">{finding.rationale}</p>
      <EvidenceBlock
        label="Personal evidence"
        ids={finding.evidence_personal}
      />
      <EvidenceBlock label="Global evidence" ids={finding.evidence_global} />
    </article>
  );
}

function EvidenceBlock({ label, ids }: { label: string; ids: string[] }) {
  if (!ids || ids.length === 0) return null;
  return (
    <div className="text-xs">
      <div className="uppercase tracking-wide text-mute mb-1">{label}</div>
      <ul className="flex flex-wrap gap-1">
        {ids.map((id) => (
          <li
            key={id}
            className="font-mono px-1.5 py-0.5 bg-stone-100 border border-stone-200 rounded"
          >
            {id}
          </li>
        ))}
      </ul>
    </div>
  );
}
