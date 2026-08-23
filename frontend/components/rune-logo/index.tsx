import Image from "next/image";

type RuneLogoProps = {
  compact?: boolean;
};

export function RuneLogo({ compact = false }: RuneLogoProps): React.ReactNode {
  return (
    <span className="inline-flex items-center gap-2.5 text-[var(--ink)]" aria-label="Rune">
      <Image src="/rune.svg" alt="" aria-hidden="true" width={28} height={28} className="size-7 dark:invert" priority />
      {!compact && <span className="text-lg font-semibold tracking-[-0.03em]">rune</span>}
    </span>
  );
}
