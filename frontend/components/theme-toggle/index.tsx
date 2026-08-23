"use client";

import { Laptop, Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

type Theme = "system" | "light" | "dark";

const themes: Theme[] = ["system", "light", "dark"];

export function ThemeToggle(): React.ReactNode {
  const [theme, setTheme] = useState<Theme>("system");

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const apply = () => {
      const dark = theme === "dark" || (theme === "system" && media.matches);
      document.documentElement.classList.toggle("dark", dark);
    };
    apply();
    media.addEventListener("change", apply);
    return () => media.removeEventListener("change", apply);
  }, [theme]);

  const Icon = theme === "system" ? Laptop : theme === "light" ? Sun : Moon;
  const labels: Record<Theme, string> = {
    system: "Tema do sistema",
    light: "Tema claro",
    dark: "Tema escuro",
  };

  return (
    <button
      type="button"
      className="grid size-10 place-items-center rounded-full border border-[var(--line)] text-[var(--muted)] transition hover:border-[var(--line-strong)] hover:text-[var(--ink)]"
      aria-label={labels[theme]}
      title={labels[theme]}
      onClick={() => setTheme(themes[(themes.indexOf(theme) + 1) % themes.length])}
    >
      <Icon aria-hidden="true" size={17} />
    </button>
  );
}
