import type { JournalEntry } from "../api/types";

interface Props {
  entries: JournalEntry[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function EntryList({ entries, selectedId, onSelect }: Props) {
  if (entries.length === 0) {
    return (
      <div className="p-4 text-mute text-sm italic">
        No entries parsed. The journal is empty or has no `###` headings.
      </div>
    );
  }

  return (
    <ul className="divide-y divide-stone-200">
      {entries.map((entry) => {
        const active = entry.id === selectedId;
        const preview = entry.text.split("\n").find((l) => l.trim()) ?? "";
        return (
          <li key={entry.id}>
            <button
              type="button"
              onClick={() => onSelect(entry.id)}
              className={`w-full text-left px-4 py-3 hover:bg-stone-100 transition-colors ${
                active ? "bg-stone-100 border-l-2 border-ink" : ""
              }`}
            >
              <div className="text-xs text-mute font-mono">
                {entry.date ?? "—"}
              </div>
              <div className="text-sm font-medium truncate">
                {entry.raw_heading}
              </div>
              <div className="text-xs text-mute truncate mt-1">{preview}</div>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
