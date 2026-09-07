// Server-only env var (no NEXT_PUBLIC_ prefix): every caller here runs on the
// server (Server Components, Server Actions, Route Handlers), so it's read
// fresh from the process environment at request time and the API origin is
// never exposed to the browser.
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

export type PartnerLabel = "PARTNER_A" | "PARTNER_B";
export type MembershipRole = "OWNER" | "MEMBER";

export interface ApiUser {
  id: string;
  email: string;
  name: string;
  picture_url: string | null;
}

export interface ApiMember {
  user_id: string;
  email: string;
  name: string;
  partner_label: PartnerLabel;
  role: MembershipRole;
}

export interface ApiHousehold {
  id: string;
  name: string;
  members: ApiMember[];
}

export interface MeResponse {
  user: ApiUser;
  household: ApiHousehold | null;
}

export async function getMe(cookieHeader: string): Promise<MeResponse | null> {
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/me`, {
      headers: { cookie: cookieHeader },
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as MeResponse;
  } catch {
    return null;
  }
}

export interface ApiResult {
  ok: boolean;
  status: number;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any;
}

export async function apiPost(
  path: string,
  cookieHeader: string,
  body?: unknown,
): Promise<ApiResult> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json", cookie: cookieHeader },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  });
  let data: unknown = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }
  return { ok: response.ok, status: response.status, data };
}
