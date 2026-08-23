import type { JobStatus } from "@/lib/enums/job-status";

export type SourceType = "upload" | "link";

export type Job = {
  id: string;
  source_type: SourceType;
  source_label: string;
  source_url: string | null;
  status: JobStatus;
  progress: number;
  message: string;
  error_code: string | null;
  error_message: string | null;
  media_title: string | null;
  media_duration: number | null;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
};

export type TranscriptWord = {
  text: string;
  start: number;
  end: number;
  confidence: number | null;
};

export type TranscriptSegment = {
  id: number;
  start: number;
  end: number;
  text: string;
  words: TranscriptWord[];
  speaker: string | null;
};

export type Transcript = {
  job_id: string;
  text: string;
  language: string | null;
  duration: number | null;
  segments: TranscriptSegment[];
};

export type RuneSystem = {
  privacy: "local_only";
  platform: string;
  library_path: string;
  model: string;
  quality: "maximum" | "faster";
  ffmpeg_ready: boolean;
  first_run_note: string;
};

export type ExportFormat = "txt" | "md" | "srt" | "vtt" | "json";
