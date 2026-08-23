import { AudioLines, CircleAlert, Clock3, FileText, Link2, RotateCcw, X } from "lucide-react";
import Link from "next/link";

import { ACTIVE_JOB_STATUSES, JobStatus } from "@/lib/enums/job-status";
import { formatCreatedAt, formatDuration } from "@/lib/helpers/format";
import type { Job } from "@/lib/types/rune";

import type { QueuePanelProps } from "./types";

const statusLabels: Record<JobStatus, string> = {
  [JobStatus.Queued]: "Na fila",
  [JobStatus.Downloading]: "Baixando",
  [JobStatus.Preparing]: "Preparando",
  [JobStatus.Transcribing]: "Transcrevendo",
  [JobStatus.Diarizing]: "Separando vozes",
  [JobStatus.Finalizing]: "Finalizando",
  [JobStatus.Completed]: "Pronto",
  [JobStatus.Failed]: "Atenção",
  [JobStatus.Cancelled]: "Cancelado",
};

function JobItem({ job, onCancel, onRetry }: { job: Job } & Pick<QueuePanelProps, "onCancel" | "onRetry">): React.ReactNode {
  const active = ACTIVE_JOB_STATUSES.has(job.status);
  const title = job.media_title || job.source_label;
  return (
    <li className="group rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-4 transition hover:border-[var(--line-strong)]">
      <div className="flex items-start gap-3">
        <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-[var(--field)] text-[var(--muted)]">
          {job.source_type === "link" ? <Link2 size={16} /> : <AudioLines size={17} />}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-[var(--ink)]">{title}</p>
              <p className="mt-1 font-mono text-[11px] text-[var(--faint)]">
                {formatDuration(job.media_duration)} · {formatCreatedAt(job.created_at)}
              </p>
            </div>
            <span className={`shrink-0 rounded-full px-2.5 py-1 text-[11px] font-bold ${job.status === JobStatus.Completed ? "bg-[var(--success-soft)] text-[var(--success)]" : job.status === JobStatus.Failed ? "bg-[var(--danger-soft)] text-[var(--danger)]" : active ? "bg-[var(--mint-soft)] text-[var(--ink)]" : "bg-[var(--field)] text-[var(--muted)]"}`}>
              {statusLabels[job.status]}
            </span>
          </div>

          {(active || job.status === JobStatus.Queued) && (
            <div className="mt-3">
              <div className="h-1.5 overflow-hidden rounded-full bg-[var(--line)]">
                <div className={`h-full rounded-full bg-[var(--mint-strong)] transition-[width] duration-500 ${job.status === JobStatus.Queued ? "w-[4%]" : ""}`} style={job.status === JobStatus.Queued ? undefined : { width: `${Math.max(job.progress, 8)}%` }} />
              </div>
              <div className="mt-2 flex items-center justify-between gap-3">
                <p className="truncate text-xs text-[var(--muted)]">{job.message}</p>
                <button type="button" onClick={() => onCancel(job.id)} className="shrink-0 rounded-md p-1 text-[var(--faint)] hover:text-[var(--ink)]" aria-label={`Cancelar ${title}`}><X size={14} /></button>
              </div>
            </div>
          )}

          {job.status === JobStatus.Completed && (
            <Link href={`/transcriptions/${job.id}`} className="mt-3 inline-flex items-center gap-1.5 text-xs font-bold text-[var(--ink)] underline decoration-[var(--mint-strong)] decoration-2 underline-offset-4">
              <FileText size={14} /> Abrir texto
            </Link>
          )}

          {job.status === JobStatus.Failed && (
            <div className="mt-3 rounded-xl bg-[var(--danger-soft)] p-3">
              <p className="flex gap-2 text-xs leading-5 text-[var(--danger)]"><CircleAlert size={14} className="mt-0.5 shrink-0" />{job.error_message || "O arquivo original não foi alterado. Tente novamente."}</p>
              <button type="button" onClick={() => onRetry(job.id)} className="mt-2 inline-flex items-center gap-1.5 text-xs font-bold text-[var(--danger)]"><RotateCcw size={13} /> Tentar novamente</button>
            </div>
          )}
        </div>
      </div>
    </li>
  );
}

export function QueuePanel({ jobs, loading, connected, onCancel, onRetry }: QueuePanelProps): React.ReactNode {
  const working = jobs.filter((job) => ACTIVE_JOB_STATUSES.has(job.status)).length;
  const waiting = jobs.filter((job) => job.status === JobStatus.Queued).length;
  return (
    <aside aria-labelledby="queue-title" className="rounded-[28px] border border-[var(--line)] bg-[color:var(--surface)/0.72] p-4 shadow-[var(--shadow-sm)] sm:p-5">
      <div className="mb-4 flex items-center justify-between gap-3 px-1">
        <div>
          <h2 id="queue-title" className="text-base font-bold tracking-[-0.02em] text-[var(--ink)]">Fila</h2>
          <p className="mt-0.5 text-xs text-[var(--muted)]">{working > 0 ? `${working} processando` : waiting > 0 ? `${waiting} aguardando` : `${jobs.length} itens`}</p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-[var(--field)] px-2.5 py-1.5 text-[11px] font-semibold text-[var(--muted)]">
          <span className={`size-1.5 rounded-full ${connected ? "bg-[var(--success)]" : "bg-[var(--warning)]"}`} />
          {connected ? "Ao vivo" : "Reconectando"}
        </span>
      </div>
      {loading ? (
        <div className="grid gap-2"><div className="h-28 animate-pulse rounded-2xl bg-[var(--field)]" /><div className="h-28 animate-pulse rounded-2xl bg-[var(--field)]" /></div>
      ) : jobs.length === 0 ? (
        <div className="grid min-h-64 place-items-center rounded-2xl border border-dashed border-[var(--line)] bg-[var(--field)] px-6 text-center">
          <div>
            <span className="mx-auto mb-4 grid size-12 place-items-center rounded-full bg-[var(--surface)] text-[var(--muted)] shadow-sm"><Clock3 size={20} /></span>
            <p className="font-semibold text-[var(--ink)]">Sua fila está livre</p>
            <p className="mt-1 text-sm leading-5 text-[var(--muted)]">Os itens aparecem aqui assim que você adiciona.</p>
          </div>
        </div>
      ) : (
        <ul className="grid max-h-[650px] gap-2 overflow-y-auto pr-0.5">
          {jobs.map((job) => <JobItem key={job.id} job={job} onCancel={onCancel} onRetry={onRetry} />)}
        </ul>
      )}
    </aside>
  );
}
