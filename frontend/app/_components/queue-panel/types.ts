import type { Job } from "@/lib/types/rune";

export type QueuePanelProps = {
  jobs: Job[];
  loading: boolean;
  connected: boolean;
  onCancel: (jobId: string) => Promise<void>;
  onRetry: (jobId: string) => Promise<void>;
};
