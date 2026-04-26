import { useEffect, useMemo, useState } from "react";
import type { JournalEntry } from "../api/types";
import { parseJournal } from "../lib/parseJournal";
import {
  loadBundledSample,
  pickJournal,
  type LoadedJournal,
} from "../lib/loadJournal";
import { EntryList } from "../components/EntryList";

interface Props {
  selectedEntry: JournalEntry | null;
  onSelect: (entry: JournalEntry | null) => void;
}

export function JournalView({ selectedEntry, onSelect }: Props) {
  const [journal, setJournal] = useState<LoadedJournal>(() => loadBundledSample());
  const [error, setError] = useState<string | null>(null);

  const entries = useMemo(
    () => parseJournal(journal.markdown, journal.sourcePath),
    [journal],
  );

  useEffect(() => {
    if (entries.length === 0) {
      onSelect(null);
      return;
    }
    if (!selectedEntry || !entries.some((e) => e.id === selectedEntry.id)) {
      onSelect(entries[0]);
    }
  }, [entries, selectedEntry, onSelect]);

  async function handlePick() {
    setError(null);
    try {
      const next = await pickJournal();
      if (next) setJournal(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  function handleResetSample() {
    setError(null);
    setJournal(loadBundledSample());
  }

  return (
    <aside className="h-full w-96 border-r border-stone-200 flex flex-col bg-white">
      <div className="px-4 py-3 border-b border-stone-200 flex items-center gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-xs uppercase tracking-wide text-mute">Journal</div>
          <div className="text-xs font-mono truncate text-mute" title={journal.sourcePath}>
            {journal.sourcePath}
          </div>
        </div>
        <button
          type="button"
          onClick={handlePick}
          className="text-xs px-2 py-1 border border-stone-300 rounded hover:bg-stone-100"
        >
          Open…
        </button>
        <button
          type="button"
          onClick={handleResetSample}
          className="text-xs px-2 py-1 border border-stone-300 rounded hover:bg-stone-100"
        >
          Sample
        </button>
      </div>
      {error && (
        <div className="px-4 py-2 text-xs text-red-700 bg-red-50 border-b border-red-200">
          {error}
        </div>
      )}
      <div className="flex-1 overflow-y-auto">
        <EntryList
          entries={entries}
          selectedId={selectedEntry?.id ?? null}
          onSelect={(id) => {
            const next = entries.find((e) => e.id === id) ?? null;
            onSelect(next);
          }}
        />
      </div>
    </aside>
  );
}
