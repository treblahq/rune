import { AppHeader } from "@/components/app-header";

import { TranscriptWorkspace } from "./_components/transcript-workspace";

export default async function TranscriptionPage({
  params,
}: {
  params: Promise<{ jobId: string }>;
}): Promise<React.ReactNode> {
  const { jobId } = await params;
  return (
    <div className="min-h-dvh bg-[var(--paper)]">
      <AppHeader />
      <TranscriptWorkspace jobId={jobId} />
    </div>
  );
}
