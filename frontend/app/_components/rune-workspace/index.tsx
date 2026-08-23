"use client";

import { CheckCircle2, Cpu, HardDrive, Sparkles } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { runeApi } from "@/lib/services/rune-api";
import type { Job, RuneSystem } from "@/lib/types/rune";

import { InputComposer } from "../input-composer";
import { QueuePanel } from "../queue-panel";

export function RuneWorkspace(): React.ReactNode {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [system, setSystem] = useState<RuneSystem | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [connected, setConnected] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setJobs(await runeApi.listJobs());
      setConnected(true);
      setNotice(null);
    } catch {
      setConnected(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const initialLoad = window.setTimeout(() => {
      void refresh();
      void runeApi.getSystem().then(setSystem).catch(() => undefined);
    }, 0);
    const source = new EventSource(runeApi.eventUrl());
    source.addEventListener("ready", () => setConnected(true));
    source.addEventListener("queue", () => void refresh());
    source.onerror = () => setConnected(false);
    const fallback = window.setInterval(() => void refresh(), 3_000);
    return () => {
      window.clearTimeout(initialLoad);
      source.close();
      window.clearInterval(fallback);
    };
  }, [refresh]);

  const add = async (links: string[], files: File[]) => {
    setBusy(true);
    setNotice(null);
    try {
      await Promise.all([
        links.length > 0 ? runeApi.addLinks(links) : Promise.resolve([]),
        files.length > 0 ? runeApi.addFiles(files) : Promise.resolve([]),
      ]);
      await refresh();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Não foi possível adicionar estes itens.");
    } finally {
      setBusy(false);
    }
  };

  const cancel = async (jobId: string) => { await runeApi.cancelJob(jobId); await refresh(); };
  const retry = async (jobId: string) => { await runeApi.retryJob(jobId); await refresh(); };

  return (
    <main className="mx-auto w-full max-w-[1240px] flex-1 px-5 pb-16 pt-12 sm:px-8 sm:pt-16 lg:pt-20">
      <div className="grid items-start gap-10 lg:grid-cols-[minmax(0,1.55fr)_minmax(330px,0.75fr)] lg:gap-8">
        <div>
          <div className="mb-8 max-w-3xl">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-[var(--line)] bg-[var(--surface)] px-3 py-1.5 text-xs font-bold text-[var(--muted)] shadow-sm">
              <Sparkles aria-hidden="true" size={14} className="text-[var(--success)]" />
              Vídeo e áudio para texto
            </div>
            <h1 className="max-w-[760px] text-[clamp(2.6rem,7vw,5.4rem)] font-semibold leading-[0.94] tracking-[-0.065em] text-[var(--ink)]">
              Seu áudio, em texto. <span className="text-[var(--muted)]">Sem sair do seu Mac.</span>
            </h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-[var(--muted)] sm:text-lg">
              Cole links, envie arquivos e deixe a fila rodar. O Rune cuida de cada item separadamente, no seu computador.
            </p>
          </div>

          {notice && <div role="alert" className="mb-4 rounded-2xl border border-[var(--danger-line)] bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger)]">{notice}</div>}
          <InputComposer busy={busy} onAdd={add} />

          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <div className="flex items-center gap-3 rounded-2xl px-2 py-2 text-sm text-[var(--muted)]"><Cpu size={17} className="text-[var(--ink)]" /><span><strong className="block text-[var(--ink)]">Whisper large-v3</strong>Qualidade máxima local</span></div>
            <div className="flex items-center gap-3 rounded-2xl px-2 py-2 text-sm text-[var(--muted)]"><HardDrive size={17} className="text-[var(--ink)]" /><span><strong className="block text-[var(--ink)]">Biblioteca própria</strong>{system ? "Documents/Rune" : "Fora do projeto"}</span></div>
            <div className="flex items-center gap-3 rounded-2xl px-2 py-2 text-sm text-[var(--muted)]"><CheckCircle2 size={17} className="text-[var(--ink)]" /><span><strong className="block text-[var(--ink)]">Original intacto</strong>Edite só o texto</span></div>
          </div>

          {system && (
            <p className="mt-8 text-xs leading-5 text-[var(--faint)]">
              Na primeira transcrição, o Rune baixa o modelo gratuito uma única vez. Depois, funciona inteiramente neste Mac.
            </p>
          )}
        </div>
        <div className="lg:sticky lg:top-6"><QueuePanel jobs={jobs} loading={loading} connected={connected} onCancel={cancel} onRetry={retry} /></div>
      </div>
    </main>
  );
}
