"use client";

import { useState, useTransition } from "react";

import { createInvite } from "@/app/dashboard/actions";
import { Button } from "@/components/ui/button";

export function InvitePanel() {
  const [pending, startTransition] = useTransition();
  const [inviteUrl, setInviteUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function generate() {
    startTransition(async () => {
      const result = await createInvite();
      if (result.error) {
        setError(result.error);
        setInviteUrl(null);
      } else {
        setInviteUrl(result.inviteUrl ?? null);
        setError(null);
      }
    });
  }

  return (
    <div className="flex flex-col gap-2">
      <Button variant="outline" size="sm" disabled={pending} onClick={generate}>
        {pending ? "Generating…" : "Invite partner"}
      </Button>
      {inviteUrl && (
        <input
          readOnly
          value={inviteUrl}
          onFocus={(event) => event.currentTarget.select()}
          className="w-full rounded-md border border-zinc-300 px-3 py-2 font-mono text-xs dark:border-zinc-700 dark:bg-zinc-900"
        />
      )}
      {inviteUrl && (
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          Send this link to the other partner. It can be used once.
        </p>
      )}
      {error && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      )}
    </div>
  );
}
