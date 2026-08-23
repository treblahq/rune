export enum JobStatus {
  Queued = "queued",
  Downloading = "downloading",
  Preparing = "preparing",
  Transcribing = "transcribing",
  Diarizing = "diarizing",
  Finalizing = "finalizing",
  Completed = "completed",
  Failed = "failed",
  Cancelled = "cancelled",
}

export const ACTIVE_JOB_STATUSES = new Set<JobStatus>([
  JobStatus.Downloading,
  JobStatus.Preparing,
  JobStatus.Transcribing,
  JobStatus.Diarizing,
  JobStatus.Finalizing,
]);
