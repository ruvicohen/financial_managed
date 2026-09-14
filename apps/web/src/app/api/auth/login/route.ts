import { NextResponse, type NextRequest } from "next/server";

// Redirects to this app's own origin (rewritten to the backend by
// next.config.ts) rather than the API's origin directly: the OAuth `state`
// cookie the backend sets here must be on the same host it reads it back
// from in the callback, and in a split-host deployment those are different
// hosts unless both hops go through this proxy.

function safeNext(value: string | null): string {
  if (value && value.startsWith("/") && !value.startsWith("//")) return value;
  return "/dashboard";
}

export function GET(request: NextRequest): NextResponse {
  const next = safeNext(request.nextUrl.searchParams.get("next"));
  const target = new URL(
    `/api/v1/auth/google/login?next=${encodeURIComponent(next)}`,
    request.url,
  );
  return NextResponse.redirect(target, { status: 302 });
}
