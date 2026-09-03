// Server-only env var (no NEXT_PUBLIC_ prefix): this fetch runs in a Server
// Component, so it's read fresh from the process environment at request
// time. A NEXT_PUBLIC_-prefixed var would instead be inlined at build time,
// which breaks overriding it per-environment (e.g. via docker-compose)
// without rebuilding the image.
const API_URL = process.env.API_URL ?? "http://localhost:8000";

export interface HealthStatus {
  status: string;
}

export async function getHealth(): Promise<HealthStatus | null> {
  try {
    const response = await fetch(`${API_URL}/health`, { cache: "no-store" });
    if (!response.ok) return null;
    return (await response.json()) as HealthStatus;
  } catch {
    return null;
  }
}
