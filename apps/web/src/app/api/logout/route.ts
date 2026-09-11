import { NextResponse, type NextRequest } from "next/server";

import { API_URL } from "@/lib/api-url";
import { SESSION_COOKIE_NAME } from "@/lib/session-cookie";

export async function POST(request: NextRequest): Promise<NextResponse> {
  const cookieHeader = request.headers.get("cookie") ?? "";
  try {
    await fetch(`${API_URL}/api/v1/auth/logout`, {
      method: "POST",
      headers: { cookie: cookieHeader },
      cache: "no-store",
    });
  } catch {
    // Even if the backend call fails, still clear the local cookie below.
  }
  const response = NextResponse.redirect(new URL("/login", request.url), { status: 303 });
  response.cookies.set(SESSION_COOKIE_NAME, "", { path: "/", maxAge: 0 });
  return response;
}
