// Base URL of the FastAPI backend, read server-side only (see API_URL in
// apps/web/.env.example). Render's blueprint `fromService` property
// `hostport` (render.yaml) resolves to a bare `host:port` with no scheme,
// since Render's private network is always plain HTTP internally - e.g.
// `financial-managed-api:8000`. Handed to `fetch`/`NextResponse.redirect` as
// -is, a browser parses the part before ":" as the URL scheme instead of a
// host, which fails with "the scheme does not have a registered handler".
// Normalize by prepending http:// whenever no scheme is present.
function normalize(url: string): string {
  return /^[a-z][a-z0-9+.-]*:\/\//i.test(url) ? url : `http://${url}`;
}

export const API_URL = normalize(process.env.API_URL ?? "http://localhost:8000");
