"use client";

import { useState, useTransition } from "react";

import { acceptInvite } from "@/app/dashboard/actions";
import { Button } from "@/components/ui/button";

export function AcceptInvite({ token }: { token: string }) {
  const [pending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  function join() {
    startTransition(async () => {
      const result = await acceptInvite(token);
      if (result?.error) setError(result.error);
    });
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <Button size="lg" disabled={pending} onClick={join}>
        {pending ? "Joining…" : "Join household"}
      </Button>
      {error && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      )}
    </div>
  );
}
