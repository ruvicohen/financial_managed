import { redirect } from "next/navigation";

import { buttonVariants } from "@/components/ui/button";
import { getCurrentUser } from "@/lib/auth";
import { cn } from "@/lib/utils";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const me = await getCurrentUser();
  if (me) redirect("/dashboard");

  const { error } = await searchParams;

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 bg-zinc-50 p-6 dark:bg-black">
      <div className="flex w-full max-w-sm flex-col items-center gap-6 rounded-xl border border-zinc-200 bg-white p-8 dark:border-zinc-800 dark:bg-zinc-950">
        <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
          Financial Managed
        </h1>
        <p className="text-center text-sm text-zinc-600 dark:text-zinc-400">
          Sign in with the Google account you use for this household.
        </p>
        {error === "not_authorized" && (
          <p
            role="alert"
            className="w-full rounded-md bg-red-50 px-3 py-2 text-center text-sm text-red-700 dark:bg-red-950 dark:text-red-300"
          >
            That Google account isn&apos;t authorized for this household.
          </p>
        )}
        <a
          href="/api/auth/login?next=/dashboard"
          className={cn(buttonVariants({ size: "lg" }), "w-full")}
        >
          Sign in with Google
        </a>
      </div>
    </main>
  );
}
