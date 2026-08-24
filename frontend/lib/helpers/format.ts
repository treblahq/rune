export function formatDuration(value: number | null): string {
  if (value === null || !Number.isFinite(value)) {
    return "Sem duração";
  }
  const total = Math.max(0, Math.round(value));
  const hours = Math.floor(total / 3_600);
  const minutes = Math.floor((total % 3_600) / 60);
  const seconds = total % 60;
  return hours > 0
    ? `${hours}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
    : `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

export function splitMediaLinks(value: string): string[] {
  return [...new Set(value.split(/\s+/).map((item) => item.trim()).filter(Boolean))];
}

export function formatCreatedAt(value: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
