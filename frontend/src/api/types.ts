// Mirrors backend/schemas.py. Keep field names and types in sync.

export type DistortionLabel =
  | "catastrophizing"
  | "all_or_nothing"
  | "emotional_reasoning"
  | "mind_reading"
  | "fortune_telling"
  | "personalization"
  | "should_statements"
  | "labeling"
  | "magnification_minimization"
  | "mental_filter"
  | "disqualifying_positive"
  | "overgeneralization";

export type PersonaName = "marcus_aurelius" | "hunter_s_thompson";

export interface JournalEntry {
  id: string;
  date: string | null;
  raw_heading: string;
  text: string;
  source_path: string;
}

export interface Span {
  start: number;
  end: number;
}

export interface DistortionFinding {
  label: DistortionLabel;
  span: Span;
  quote: string;
  rationale: string;
  evidence_global: string[];
  evidence_personal: string[];
  confidence: number;
}

export interface IngestRequest {
  source_path?: string;
  markdown?: string;
}

export interface IngestResponse {
  entries: JournalEntry[];
}

export interface DetectRequest {
  entry_id?: string;
  text?: string;
}
