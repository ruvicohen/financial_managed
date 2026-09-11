import { NextResponse, type NextRequest } from "next/server";

import { API_URL } from "@/lib/api-url";

// Keeps the API origin server-side: the browser navigates here, and we bounce
// it to the backend's Google login endpoint.

function safeNext(value: string | null): string {
  if (value && value.startsWith("/") && !value.startsWith("//")) return value;
  return "/dashboard";
}

export function GET(request: NextRequest): NextResponse {
  const next = safeNext(request.nextUrl.searchParams.get("next"));
  const target = `${API_URL}/api/v1/auth/google/login?next=${encodeURIComponent(next)}`;
  return NextResponse.redirect(target, { status: 302 });
}
