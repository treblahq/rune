import Link from "next/link";
import { ShieldCheck } from "lucide-react";

import { RuneLogo } from "@/components/rune-logo";
import { ThemeToggle } from "@/components/theme-toggle";

type AppHeaderProps = {
  compact?: boolean;
};

export function AppHeader({ compact = false }: AppHeaderProps): React.ReactNode {
  return (
    <header className="border-b border-[var(--line)] bg-[color:var(--paper)/0.92]">
      <div className="mx-auto flex h-18 w-full max-w-[1240px] items-center justify-between px-5 sm:px-8">
        <Link href="/" className="rounded-md" aria-label="Voltar ao início do Rune">
          <RuneLogo compact={compact} />
        </Link>
        <div className="flex items-center gap-2.5 sm:gap-4">
          <span className="hidden items-center gap-2 text-sm font-medium text-[var(--muted)] sm:inline-flex">
            <ShieldCheck aria-hidden="true" size={16} className="text-[var(--success)]" />
            Processando neste Mac
          </span>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
