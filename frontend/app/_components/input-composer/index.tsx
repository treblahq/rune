"use client";

import { FileAudio, Files, Link2, Plus, Upload, X } from "lucide-react";
import { useRef, useState } from "react";

import { splitMediaLinks } from "@/lib/helpers/format";

import type { InputComposerProps } from "./types";

type Mode = "links" | "files";

export function InputComposer({ busy, onAdd }: InputComposerProps): React.ReactNode {
  const [mode, setMode] = useState<Mode>("links");
  const [linkDraft, setLinkDraft] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const links = splitMediaLinks(linkDraft);

  const addFiles = (incoming: File[]) => {
    setFiles((current) => {
      const keys = new Set(current.map((file) => `${file.name}:${file.size}:${file.lastModified}`));
      return [...current, ...incoming.filter((file) => !keys.has(`${file.name}:${file.size}:${file.lastModified}`))];
    });
  };

  const submit = async () => {
    if (busy || (links.length === 0 && files.length === 0)) return;
    await onAdd(links, files);
    setLinkDraft("");
    setFiles([]);
  };

  return (
    <section className="overflow-hidden rounded-[28px] border border-[var(--line)] bg-[var(--surface)] shadow-[var(--shadow-lg)]">
      <div className="flex border-b border-[var(--line)] px-5 pt-4 sm:px-7">
        {(["links", "files"] as const).map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setMode(item)}
            className={`relative flex h-12 items-center gap-2 px-3 text-sm font-semibold transition ${mode === item ? "text-[var(--ink)]" : "text-[var(--muted)] hover:text-[var(--ink)]"}`}
          >
            {item === "links" ? <Link2 size={17} /> : <Files size={17} />}
            {item === "links" ? "Colar links" : "Enviar arquivos"}
            {item === "files" && files.length > 0 && (
              <span className="rounded-full bg-[var(--mint-soft)] px-2 py-0.5 font-mono text-[11px] text-[var(--ink)]">{files.length}</span>
            )}
            {mode === item && <span className="absolute inset-x-2 bottom-0 h-0.5 rounded-full bg-[var(--ink)]" />}
          </button>
        ))}
      </div>

      <div className="p-5 sm:p-7">
        {mode === "links" ? (
          <div>
            <label htmlFor="media-links" className="mb-2 block text-sm font-semibold text-[var(--ink)]">
              Links de vídeo ou áudio
            </label>
            <textarea
              id="media-links"
              value={linkDraft}
              onChange={(event) => setLinkDraft(event.target.value)}
              rows={5}
              placeholder={"Cole um ou vários links. Um por linha."}
              className="w-full resize-none rounded-2xl border border-[var(--line)] bg-[var(--field)] px-4 py-3.5 text-[15px] leading-6 text-[var(--ink)] outline-none transition placeholder:text-[var(--faint)] focus:border-[var(--ink)] focus:ring-3 focus:ring-[var(--focus)]"
            />
            <p className="mt-2 text-xs leading-5 text-[var(--muted)]">
              YouTube, Vimeo, podcasts e links diretos de mídia. Listas não são importadas por acidente.
            </p>
          </div>
        ) : (
          <div
            className={`grid min-h-44 place-items-center rounded-2xl border border-dashed px-5 text-center transition ${dragging ? "border-[var(--ink)] bg-[var(--mint-soft)]" : "border-[var(--line-strong)] bg-[var(--field)]"}`}
            onDragEnter={(event) => { event.preventDefault(); setDragging(true); }}
            onDragOver={(event) => event.preventDefault()}
            onDragLeave={() => setDragging(false)}
            onDrop={(event) => {
              event.preventDefault();
              setDragging(false);
              addFiles(Array.from(event.dataTransfer.files));
            }}
          >
            <div className="py-6">
              <span className="mx-auto mb-3 grid size-11 place-items-center rounded-full bg-[var(--mint-soft)] text-[var(--ink)]"><Upload size={19} /></span>
              <p className="font-semibold text-[var(--ink)]">Solte seus vídeos e áudios aqui</p>
              <p className="mt-1 text-sm text-[var(--muted)]">ou escolha quantos arquivos quiser</p>
              <button type="button" onClick={() => inputRef.current?.click()} className="mt-4 rounded-full border border-[var(--line-strong)] bg-[var(--surface)] px-4 py-2 text-sm font-semibold text-[var(--ink)] hover:border-[var(--ink)]">
                Escolher arquivos
              </button>
              <input ref={inputRef} className="sr-only" type="file" multiple accept="audio/*,video/*" onChange={(event) => addFiles(Array.from(event.target.files ?? []))} />
            </div>
          </div>
        )}

        {files.length > 0 && (
          <ul className="mt-4 grid gap-2" aria-label="Arquivos selecionados">
            {files.map((file, index) => (
              <li key={`${file.name}:${file.lastModified}`} className="flex items-center gap-3 rounded-xl bg-[var(--field)] px-3 py-2.5 text-sm">
                <FileAudio size={16} className="shrink-0 text-[var(--muted)]" />
                <span className="min-w-0 flex-1 truncate font-medium text-[var(--ink)]">{file.name}</span>
                <button type="button" aria-label={`Remover ${file.name}`} onClick={() => setFiles((current) => current.filter((_, currentIndex) => currentIndex !== index))} className="rounded-full p-1 text-[var(--muted)] hover:bg-[var(--line)] hover:text-[var(--ink)]"><X size={15} /></button>
              </li>
            ))}
          </ul>
        )}

        <div className="mt-6 flex flex-col gap-3 border-t border-[var(--line)] pt-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2 text-xs font-medium text-[var(--muted)]">
            <span className="size-2 rounded-full bg-[var(--success)]" />
            Qualidade máxima · tudo fica neste Mac
          </div>
          <button
            type="button"
            disabled={busy || (links.length === 0 && files.length === 0)}
            onClick={submit}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-full bg-[var(--mint)] px-6 text-sm font-bold text-[#15221f] shadow-sm transition hover:-translate-y-0.5 hover:bg-[var(--mint-strong)] disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:translate-y-0"
          >
            {busy ? <span className="size-4 animate-spin rounded-full border-2 border-current border-r-transparent" /> : <Plus size={18} strokeWidth={2.5} />}
            {busy ? "Adicionando…" : "Adicionar à fila"}
          </button>
        </div>
      </div>
    </section>
  );
}
