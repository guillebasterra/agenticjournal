import { readTextFile } from "@tauri-apps/plugin-fs";
import { open } from "@tauri-apps/plugin-dialog";
import sampleJournal from "../fixtures/sample_journal.md?raw";

export interface LoadedJournal {
  markdown: string;
  sourcePath: string;
}

/**
 * Returns the bundled sample journal. Used as the default on first launch so
 * the app is functional without any user-side configuration.
 */
export function loadBundledSample(): LoadedJournal {
  return {
    markdown: sampleJournal,
    sourcePath: "bundled:sample_journal.md",
  };
}

/**
 * Open a markdown file picker via the Tauri dialog plugin and read the
 * selected file via the Tauri fs plugin. Returns null if the user cancels.
 */
export async function pickJournal(): Promise<LoadedJournal | null> {
  const selected = await open({
    multiple: false,
    directory: false,
    filters: [{ name: "Markdown", extensions: ["md", "markdown", "txt"] }],
  });
  if (!selected || typeof selected !== "string") return null;
  const markdown = await readTextFile(selected);
  return { markdown, sourcePath: selected };
}
