import { getHealth } from "@/lib/api";

export default async function Home() {
  const health = await getHealth();

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 bg-zinc-50 font-sans dark:bg-black">
      <h1 className="text-3xl font-semibold text-black dark:text-zinc-50">
        Financial Managed
      </h1>
      <p className="text-lg text-zinc-600 dark:text-zinc-400">
        Backend status:{" "}
        <span
          className={
            health?.status === "ok"
              ? "font-medium text-green-600 dark:text-green-400"
              : "font-medium text-red-600 dark:text-red-400"
          }
        >
          {health?.status ?? "unreachable"}
        </span>
      </p>
    </div>
  );
}
