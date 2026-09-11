import Link from "next/link";
import { redirect } from "next/navigation";

import { AcceptInvite } from "@/components/accept-invite";
import { buttonVariants } from "@/components/ui/button";
import { getCurrentUser } from "@/lib/auth";
import { cn } from "@/lib/utils";

export default async function JoinPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token } = await searchParams;
  if (!token) redirect("/dashboard");

  const me = await getCurrentUser();
  if (!me) {
    redirect(`/api/auth/login?next=${encodeURIComponent(`/join?token=${token}`)}`);
  }

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 p-6">
      <div className="flex w-full max-w-sm flex-col items-center gap-4 rounded-xl border border-zinc-200 bg-white p-8 dark:border-zinc-800 dark:bg-zinc-950">
        {me.household ? (
          <>
            <p className="text-center text-sm text-zinc-600 dark:text-zinc-400">
              You already belong to the household “{me.household.name}”.
            </p>
            <Link href="/dashboard" className={cn(buttonVariants({ size: "lg" }), "w-full")}>
              Go to dashboard
            </Link>
          </>
        ) : (
          <>
            <h1 className="text-xl font-semibold text-black dark:text-zinc-50">
              Join household
            </h1>
            <p className="text-center text-sm text-zinc-600 dark:text-zinc-400">
              You&apos;ve been invited to share a household workspace.
            </p>
            <AcceptInvite token={token} />
          </>
        )}
      </div>
    </main>
  );
}
