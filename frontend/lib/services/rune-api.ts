import type { ExportFormat, Job, RuneSystem, Transcript } from "@/lib/types/rune";

const API_URL = process.env.NEXT_PUBLIC_RUNE_API_URL ?? "http://127.0.0.1:43891";

type ErrorPayload = { error?: { code?: string; message?: string } };

async function runeRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: init?.body instanceof FormData
      ? init.headers
      : { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as ErrorPayload;
    const error = new Error(
      payload.error?.message ?? "O Rune não conseguiu concluir esta ação.",
    );
    Object.assign(error, { code: payload.error?.code ?? "request_failed" });
    throw error;
  }
  return response.json() as Promise<T>;
}

export const runeApi = {
  baseUrl: API_URL,
  listJobs: () => runeRequest<Job[]>("/api/jobs"),
  getJob: (jobId: string) => runeRequest<Job>(`/api/jobs/${jobId}`),
  getSystem: () => runeRequest<RuneSystem>("/api/system"),
  addLinks: (urls: string[]) =>
    runeRequest<Job[]>("/api/jobs/links", { method: "POST", body: JSON.stringify({ urls }) }),
  addFiles: (files: File[]) => {
    const body = new FormData();
    files.forEach((file) => body.append("files", file));
    return runeRequest<Job[]>("/api/jobs/uploads", { method: "POST", body });
  },
  cancelJob: (jobId: string) =>
    runeRequest<Job>(`/api/jobs/${jobId}/cancel`, { method: "POST" }),
  retryJob: (jobId: string) =>
    runeRequest<Job>(`/api/jobs/${jobId}/retry`, { method: "POST" }),
  getTranscript: (jobId: string) =>
    runeRequest<Transcript>(`/api/jobs/${jobId}/transcript`),
  saveTranscript: (jobId: string, text: string) =>
    runeRequest<Transcript>(`/api/jobs/${jobId}/transcript`, {
      method: "PATCH",
      body: JSON.stringify({ text }),
    }),
  exportUrl: (jobId: string, format: ExportFormat) =>
    `${API_URL}/api/jobs/${jobId}/export/${format}`,
  mediaUrl: (jobId: string) => `${API_URL}/api/jobs/${jobId}/media`,
  eventUrl: () => `${API_URL}/api/events`,
};
