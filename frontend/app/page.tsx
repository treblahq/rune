import { AppHeader } from "@/components/app-header";

import { RuneWorkspace } from "./_components/rune-workspace";

export default function Home(): React.ReactNode {
  return (
    <div className="flex min-h-dvh flex-col bg-[var(--paper)]">
      <AppHeader />
      <RuneWorkspace />
    </div>
  );
}
