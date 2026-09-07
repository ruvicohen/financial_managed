import { NextResponse, type NextRequest } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

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
  response.cookies.set("fm_session", "", { path: "/", maxAge: 0 });
  return response;
}
