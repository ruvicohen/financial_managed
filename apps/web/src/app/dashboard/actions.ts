"use server";

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { apiPost } from "@/lib/api";

async function cookieHeader(): Promise<string> {
  return (await cookies()).toString();
}

export interface CreateHouseholdState {
  error?: string;
}

export async function createHouseholdAction(
  _prev: CreateHouseholdState,
  formData: FormData,
): Promise<CreateHouseholdState> {
  const name = String(formData.get("name") ?? "").trim();
  if (!name) return { error: "Please enter a household name." };

  const res = await apiPost("/api/v1/households", await cookieHeader(), { name });
  if (!res.ok) {
    return {
      error:
        res.status === 409
          ? "You already belong to a household."
          : "Could not create the household.",
    };
  }
  revalidatePath("/dashboard");
  redirect("/dashboard");
}

export async function createInvite(): Promise<{ inviteUrl?: string; error?: string }> {
  const res = await apiPost("/api/v1/households/current/invitations", await cookieHeader());
  if (!res.ok) {
    return {
      error:
        res.status === 409
          ? "There is already a pending invite (or the household is full)."
          : "Could not create an invite link.",
    };
  }
  return { inviteUrl: String(res.data?.invite_url ?? "") };
}

export async function acceptInvite(token: string): Promise<{ error: string } | undefined> {
  const res = await apiPost("/api/v1/households/invitations/accept", await cookieHeader(), {
    token,
  });
  if (!res.ok) {
    if (res.status === 409) return { error: "You already belong to a household." };
    return { error: "This invite link is invalid or has expired." };
  }
  revalidatePath("/dashboard");
  redirect("/dashboard");
}
