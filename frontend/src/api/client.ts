import mockFindings from "../fixtures/mock_findings.json";
import type {
  DetectRequest,
  DistortionFinding,
  IngestRequest,
  IngestResponse,
} from "./types";

const DEFAULT_BASE_URL = "http://localhost:8000";

export function apiBaseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? DEFAULT_BASE_URL;
}

export function isMockMode(): boolean {
  return import.meta.env.VITE_USE_MOCK_DETECT === "1";
}

async function postJson<TIn, TOut>(path: string, body: TIn): Promise<TOut> {
  const res = await fetch(`${apiBaseUrl()}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`POST ${path} ${res.status}: ${text || res.statusText}`);
  }
  return (await res.json()) as TOut;
}

export function ingest(req: IngestRequest): Promise<IngestResponse> {
  return postJson<IngestRequest, IngestResponse>("/ingest", req);
}

export interface DetectStreamHandlers {
  onFinding: (finding: DistortionFinding) => void;
  onError?: (err: Error) => void;
  onDone?: () => void;
  signal?: AbortSignal;
}

/**
 * POST /detect with SSE streaming. Each `data:` frame is parsed as a
 * DistortionFinding and surfaced via onFinding. The backend is expected to
 * send `event: done` (or close the stream) when finished.
 */
export async function detectStream(
  req: DetectRequest,
  handlers: DetectStreamHandlers,
): Promise<void> {
  if (isMockMode()) {
    return mockDetectStream(handlers);
  }

  const res = await fetch(`${apiBaseUrl()}/detect`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(req),
    signal: handlers.signal,
  });

  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => "");
    throw new Error(`POST /detect ${res.status}: ${text || res.statusText}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let sepIdx: number;
      while ((sepIdx = buffer.indexOf("\n\n")) !== -1) {
        const frame = buffer.slice(0, sepIdx);
        buffer = buffer.slice(sepIdx + 2);
        dispatchSseFrame(frame, handlers);
      }
    }
    if (buffer.trim().length > 0) {
      dispatchSseFrame(buffer, handlers);
    }
    handlers.onDone?.();
  } catch (err) {
    handlers.onError?.(err instanceof Error ? err : new Error(String(err)));
  }
}

function dispatchSseFrame(frame: string, handlers: DetectStreamHandlers) {
  let event = "message";
  const dataLines: string[] = [];

  for (const line of frame.split("\n")) {
    if (line.startsWith(":") || line.length === 0) continue;
    if (line.startsWith("event:")) {
      event = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice(5).trim());
    }
  }

  const data = dataLines.join("\n");
  if (event === "done") {
    return;
  }
  if (!data) return;
  try {
    const parsed = JSON.parse(data) as DistortionFinding;
    handlers.onFinding(parsed);
  } catch (err) {
    handlers.onError?.(
      new Error(`Could not parse SSE frame as DistortionFinding: ${data}`),
    );
  }
}

async function mockDetectStream(handlers: DetectStreamHandlers): Promise<void> {
  const findings = mockFindings as DistortionFinding[];
  for (const finding of findings) {
    if (handlers.signal?.aborted) return;
    await new Promise((r) => setTimeout(r, 250));
    handlers.onFinding(finding);
  }
  handlers.onDone?.();
}
