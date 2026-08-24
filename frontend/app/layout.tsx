import "@fontsource-variable/figtree";
import "@fontsource-variable/geist-mono";
import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Rune: vídeo e áudio para texto",
  description: "Transcreva vídeos e áudios localmente, sem enviar seus arquivos para a nuvem.",
};

export default function RootLayout({ children }: LayoutProps<"/">): React.ReactNode {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className="min-h-dvh">{children}</body>
    </html>
  );
}
