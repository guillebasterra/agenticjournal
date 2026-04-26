import { useState } from "react";
import { JournalView } from "./views/JournalView";
import { DetectView } from "./views/DetectView";
import { PersonaPanelPlaceholder } from "./components/PersonaPanelPlaceholder";
import type { JournalEntry } from "./api/types";

export default function App() {
  const [selected, setSelected] = useState<JournalEntry | null>(null);

  return (
    <div className="h-screen w-screen flex bg-paper text-ink">
      <JournalView selectedEntry={selected} onSelect={setSelected} />
      <DetectView entry={selected} />
      <PersonaPanelPlaceholder />
    </div>
  );
}
