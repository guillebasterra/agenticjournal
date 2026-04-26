import type { DistortionFinding } from "../api/types";

interface Props {
  text: string;
  findings: DistortionFinding[];
  activeIndex: number | null;
  onHover: (idx: number | null) => void;
}

interface Segment {
  start: number;
  end: number;
  findingIdx: number | null;
}

function buildSegments(textLen: number, findings: DistortionFinding[]): Segment[] {
  const valid = findings
    .map((f, idx) => ({ idx, span: f.span }))
    .filter(
      ({ span }) =>
        Number.isFinite(span.start) &&
        Number.isFinite(span.end) &&
        span.start >= 0 &&
        span.end <= textLen &&
        span.end > span.start,
    )
    .sort((a, b) => a.span.start - b.span.start);

  const segments: Segment[] = [];
  let cursor = 0;
  for (const { idx, span } of valid) {
    if (span.start < cursor) continue; // skip overlaps; first writer wins
    if (span.start > cursor) {
      segments.push({ start: cursor, end: span.start, findingIdx: null });
    }
    segments.push({ start: span.start, end: span.end, findingIdx: idx });
    cursor = span.end;
  }
  if (cursor < textLen) {
    segments.push({ start: cursor, end: textLen, findingIdx: null });
  }
  return segments;
}

export function HighlightedEntry({ text, findings, activeIndex, onHover }: Props) {
  const segments = buildSegments(text.length, findings);

  return (
    <div className="prose max-w-none whitespace-pre-wrap font-serif text-base leading-relaxed text-ink">
      {segments.map((seg, i) => {
        const slice = text.slice(seg.start, seg.end);
        if (seg.findingIdx === null) {
          return <span key={i}>{slice}</span>;
        }
        const finding = findings[seg.findingIdx];
        const active = activeIndex === seg.findingIdx;
        return (
          <mark
            key={i}
            className={`dx dx-${finding.label} ${active ? "active" : ""}`}
            onMouseEnter={() => onHover(seg.findingIdx)}
            onMouseLeave={() => onHover(null)}
            title={`${finding.label} · ${(finding.confidence * 100).toFixed(0)}%`}
          >
            {slice}
          </mark>
        );
      })}
    </div>
  );
}
