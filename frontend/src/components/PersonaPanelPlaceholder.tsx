// Reserved slot for the phase-2 persona view (Marcus Aurelius / Hunter S.
// Thompson). Do not implement here — that lives in the persona-analyzer
// worktree. This component only holds layout space.

export function PersonaPanelPlaceholder() {
  return (
    <aside className="h-full w-80 border-l border-stone-200 bg-stone-50 p-4 overflow-y-auto">
      <div className="text-xs uppercase tracking-wide text-mute mb-2">
        Persona analysis
      </div>
      <div className="text-sm text-mute italic">
        Phase 2. Persona-grounded commentary will appear here once
        `/persona/analyze` is wired up.
      </div>
    </aside>
  );
}
