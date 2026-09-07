import { cookies } from "next/headers";

import { getMe, type MeResponse } from "@/lib/api";

/**
 * Resolve the signed-in user (and their household) from the request cookies.
 * Returns null when there is no valid session. The authoritative check always
 * happens here on the server; `src/proxy.ts` only does a cheap cookie-presence
 * redirect as defense in depth.
 */
export async function getCurrentUser(): Promise<MeResponse | null> {
  const cookieHeader = (await cookies()).toString();
  if (!cookieHeader) return null;
  return getMe(cookieHeader);
}
