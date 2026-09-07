import { NextResponse, type NextRequest } from "next/server";

// Cheap defense-in-depth: bounce unauthenticated visitors away from the app
// shell before it renders. The real session check happens server-side in
// `getCurrentUser()`.
export function proxy(request: NextRequest): NextResponse {
  const hasSession = request.cookies.has("fm_session");
  if (!hasSession) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.search = "";
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/dashboard/:path*"],
};
