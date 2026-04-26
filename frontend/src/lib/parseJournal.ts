import type { JournalEntry } from "../api/types";

const HEADING_RE = /^###\s+(.+?)\s*$/gm;

const MONTHS: Record<string, number> = {
  january: 1, jan: 1,
  february: 2, feb: 2,
  march: 3, mar: 3,
  april: 4, apr: 4,
  may: 5,
  june: 6, jun: 6,
  july: 7, jul: 7,
  august: 8, aug: 8,
  september: 9, sept: 9, sep: 9,
  october: 10, oct: 10,
  november: 11, nov: 11,
  december: 12, dec: 12,
};

function tryParseDate(heading: string): string | null {
  const lower = heading.toLowerCase();

  const m1 = lower.match(/(\d{1,2})\s+(\w+)(?:\s+(\d{4}))?/);
  if (m1) {
    const day = Number(m1[1]);
    const month = MONTHS[m1[2]];
    if (month) {
      const year = m1[3] ? Number(m1[3]) : new Date().getFullYear();
      return iso(year, month, day);
    }
  }

  const m2 = lower.match(/(\w+)\s+(\d{1,2})(?:,?\s+(\d{4}))?/);
  if (m2) {
    const month = MONTHS[m2[1]];
    if (month) {
      const day = Number(m2[2]);
      const year = m2[3] ? Number(m2[3]) : new Date().getFullYear();
      return iso(year, month, day);
    }
  }

  return null;
}

function iso(year: number, month: number, day: number): string {
  const mm = String(month).padStart(2, "0");
  const dd = String(day).padStart(2, "0");
  return `${year}-${mm}-${dd}`;
}

function slug(s: string, idx: number): string {
  const base = s
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .slice(0, 60);
  return base ? `${base}-${idx}` : `entry-${idx}`;
}

/**
 * Parse a markdown journal into entries by `### heading` boundaries. Mirrors
 * backend/ingest semantics so the frontend can render entries even before the
 * `/ingest` endpoint is wired up.
 */
export function parseJournal(markdown: string, sourcePath: string): JournalEntry[] {
  const matches = [...markdown.matchAll(HEADING_RE)];
  if (matches.length === 0) {
    return [];
  }

  const entries: JournalEntry[] = [];
  for (let i = 0; i < matches.length; i++) {
    const m = matches[i];
    const heading = m[1].trim();
    if (!heading) continue;

    const start = m.index! + m[0].length;
    const end = i + 1 < matches.length ? matches[i + 1].index! : markdown.length;
    const text = markdown.slice(start, end).trim();
    if (!text) continue;

    entries.push({
      id: slug(heading, i),
      date: tryParseDate(heading),
      raw_heading: heading,
      text,
      source_path: sourcePath,
    });
  }
  return entries;
}
