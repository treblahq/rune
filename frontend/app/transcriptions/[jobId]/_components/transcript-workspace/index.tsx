"use client";

import {
  ArrowLeft,
  Check,
  Clipboard,
  Clock3,
  Download,
  FileText,
  Languages,
  RotateCcw,
  Search,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { formatDuration } from "@/lib/helpers/format";
import { findReviewMoments } from "@/lib/helpers/transcript";
import { runeApi } from "@/lib/services/rune-api";
import type { ExportFormat, Job, Transcript } from "@/lib/types/rune";

import type { TranscriptWorkspaceProps } from "./types";

const exportFormats: { value: ExportFormat; label: string; detail: string }[] = [
  { value: "txt", label: "TXT", detail: "texto simples" },
  { value: "md", label: "MD", detail: "Markdown" },
  { value: "srt", label: "SRT", detail: "legendas" },
  { value: "vtt", label: "VTT", detail: "legendas web" },
  { value: "json", label: "JSON", detail: "dados completos" },
];

const videoExtensions = [".mp4", ".mov", ".mkv", ".webm", ".avi", ".mpeg", ".mpg", ".wmv"];

export function TranscriptWorkspace({ jobId }: TranscriptWorkspaceProps): React.ReactNode {
  const [job, setJob] = useState<Job | null>(null);
  const [transcript, setTranscript] = useState<Transcript | null>(null);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<"saved" | "saving" | "error">("saved");
  const [copied, setCopied] = useState(false);
  const mediaRef = useRef<HTMLMediaElement>(null);
  const lastSaved = useRef("");

  const load = useCallback(async () => {
    try {
      const [nextJob, nextTranscript] = await Promise.all([
        runeApi.getJob(jobId),
        runeApi.getTranscript(jobId),
      ]);
      setJob(nextJob);
      setTranscript(nextTranscript);
      setDraft(nextTranscript.text);
      lastSaved.current = nextTranscript.text;
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Não foi possível abrir este texto.");
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    const initialLoad = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(initialLoad);
  }, [load]);

  useEffect(() => {
    if (!transcript || draft === lastSaved.current) return;
    setSaveState("saving");
    const timer = window.setTimeout(async () => {
      try {
        await runeApi.saveTranscript(jobId, draft);
        lastSaved.current = draft;
        setSaveState("saved");
      } catch {
        setSaveState("error");
      }
    }, 700);
    return () => window.clearTimeout(timer);
  }, [draft, jobId, transcript]);

  const reviewMoments = useMemo(
    () => (transcript ? findReviewMoments(transcript) : []),
    [transcript],
  );

  const seek = (time: number) => {
    if (!mediaRef.current) return;
    mediaRef.current.currentTime = time;
    void mediaRef.current.play();
  };

  const copy = async () => {
    await navigator.clipboard.writeText(draft);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1_500);
  };

  if (loading) {
    return (
      <main className="mx-auto max-w-[1240px] px-5 py-10 sm:px-8">
        <div className="h-12 w-1/2 animate-pulse rounded-xl bg-[var(--field)]" />
        <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_340px]">
          <div className="h-[640px] animate-pulse rounded-[28px] bg-[var(--field)]" />
          <div className="h-80 animate-pulse rounded-[28px] bg-[var(--field)]" />
        </div>
      </main>
    );
  }

  if (error || !job || !transcript) {
    return (
      <main className="mx-auto grid min-h-[70dvh] max-w-xl place-items-center px-5 text-center">
        <div>
          <span className="mx-auto mb-5 grid size-14 place-items-center rounded-full bg-[var(--danger-soft)] text-[var(--danger)]"><RotateCcw size={21} /></span>
          <h1 className="text-2xl font-bold tracking-tight">Este texto não abriu</h1>
          <p className="mt-2 text-[var(--muted)]">{error}</p>
          <Link href="/" className="mt-6 inline-flex rounded-full bg-[var(--mint)] px-5 py-3 text-sm font-bold text-[#15221f]">Voltar para a fila</Link>
        </div>
      </main>
    );
  }

  const title = job.media_title || job.source_label;
  const isVideo = videoExtensions.some((extension) => job.source_label.toLowerCase().endsWith(extension));

  return (
    <main className="mx-auto w-full max-w-[1240px] px-5 pb-16 pt-7 sm:px-8 sm:pt-10">
      <Link href="/" className="inline-flex items-center gap-2 rounded-full text-sm font-semibold text-[var(--muted)] hover:text-[var(--ink)]"><ArrowLeft size={16} /> Voltar para a fila</Link>
      <div className="mt-6 flex flex-col gap-4 border-b border-[var(--line)] pb-7 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <div className="mb-2 flex items-center gap-2 text-xs font-bold text-[var(--success)]"><ShieldCheck size={15} /> Texto processado neste Mac</div>
          <h1 className="line-clamp-2 text-3xl font-semibold tracking-[-0.045em] text-[var(--ink)] sm:line-clamp-none sm:text-4xl">{title}</h1>
          <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-[var(--muted)]">
            <span className="inline-flex items-center gap-1.5"><Clock3 size={14} />{formatDuration(job.media_duration)}</span>
            <span className="inline-flex items-center gap-1.5"><Languages size={14} />{transcript.language?.toUpperCase() || "Idioma detectado"}</span>
            <span>{draft.trim().split(/\s+/).filter(Boolean).length.toLocaleString("pt-BR")} palavras</span>
          </div>
        </div>
        <button type="button" onClick={copy} className="inline-flex h-11 shrink-0 items-center justify-center gap-2 rounded-full border border-[var(--line-strong)] bg-[var(--surface)] px-4 text-sm font-bold text-[var(--ink)] shadow-sm hover:border-[var(--ink)]">
          {copied ? <Check size={16} /> : <Clipboard size={16} />}{copied ? "Copiado" : "Copiar texto"}
        </button>
      </div>

      <div className="mt-7 grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_350px]">
        <section className="overflow-hidden rounded-[28px] border border-[var(--line)] bg-[var(--surface)] shadow-[var(--shadow-sm)]">
          <div className="flex items-center justify-between border-b border-[var(--line)] px-5 py-4 sm:px-7">
            <div className="flex items-center gap-2 text-sm font-bold"><FileText size={17} /> Transcrição</div>
            <span className={`text-xs font-semibold ${saveState === "error" ? "text-[var(--danger)]" : "text-[var(--muted)]"}`}>{saveState === "saving" ? "Salvando…" : saveState === "error" ? "Não foi possível salvar" : "Salvo automaticamente"}</span>
          </div>
          <textarea value={draft} onChange={(event) => setDraft(event.target.value)} aria-label="Texto da transcrição" spellCheck className="min-h-[520px] w-full resize-y bg-transparent px-5 py-6 text-[17px] leading-8 text-[var(--ink)] outline-none sm:min-h-[660px] sm:px-8 sm:py-8" />
        </section>

        <aside className="grid gap-4 lg:sticky lg:top-5">
          <section className="overflow-hidden rounded-[24px] border border-[var(--line)] bg-[var(--surface)] shadow-[var(--shadow-sm)]">
            {isVideo ? (
              <video ref={mediaRef as React.RefObject<HTMLVideoElement | null>} src={runeApi.mediaUrl(jobId)} controls preload="metadata" className="aspect-video w-full bg-black" />
            ) : (
              <div className="p-4"><audio ref={mediaRef as React.RefObject<HTMLAudioElement | null>} src={runeApi.mediaUrl(jobId)} controls preload="metadata" className="w-full" /></div>
            )}
          </section>

          <section className="rounded-[24px] border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-sm)]">
            <div className="mb-4 flex items-center justify-between"><h2 className="flex items-center gap-2 text-sm font-bold"><Search size={16} /> Trechos para revisar</h2><span className="rounded-full bg-[var(--field)] px-2 py-1 font-mono text-[10px] text-[var(--muted)]">{reviewMoments.length}</span></div>
            {reviewMoments.length === 0 ? (
              <p className="text-sm leading-6 text-[var(--muted)]">Nenhuma palavra ficou abaixo do limite de confiança.</p>
            ) : (
              <ul className="grid max-h-56 gap-1.5 overflow-y-auto">
                {reviewMoments.slice(0, 30).map((moment, index) => (
                  <li key={`${moment.segmentId}-${moment.start}-${index}`}>
                    <button type="button" onClick={() => seek(moment.start)} className="flex w-full items-center justify-between rounded-xl bg-[var(--field)] px-3 py-2.5 text-left hover:bg-[var(--mint-soft)]">
                      <span className="truncate text-sm font-semibold text-[var(--ink)]">{moment.text || "Trecho sem texto"}</span>
                      <span className="ml-3 font-mono text-[10px] text-[var(--muted)]">{formatDuration(moment.start)}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="rounded-[24px] border border-[var(--line)] bg-[var(--surface)] p-5 shadow-[var(--shadow-sm)]">
            <h2 className="mb-4 flex items-center gap-2 text-sm font-bold"><Download size={16} /> Exportar</h2>
            <div className="grid gap-2">
              {exportFormats.map((format) => (
                <a key={format.value} href={runeApi.exportUrl(jobId, format.value)} download className="flex items-center justify-between rounded-xl border border-[var(--line)] px-3.5 py-2.5 hover:border-[var(--line-strong)] hover:bg-[var(--field)]">
                  <span className="text-sm font-bold">{format.label}</span>
                  <span className="text-xs text-[var(--muted)]">{format.detail}</span>
                </a>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </main>
  );
}
