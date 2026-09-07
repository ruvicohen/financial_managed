import { redirect } from "next/navigation";

import { CreateHouseholdForm } from "@/components/create-household-form";
import { InvitePanel } from "@/components/invite-panel";
import { LogoutButton } from "@/components/logout-button";
import { getCurrentUser } from "@/lib/auth";

export default async function DashboardPage() {
  const me = await getCurrentUser();
  if (!me) redirect("/login");

  const household = me.household;
  const isOwner = household?.members.some(
    (m) => m.role === "OWNER" && m.user_id === me.user.id,
  );
  const canInvite = Boolean(household && isOwner && household.members.length < 2);

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-8 p-6">
      <header className="flex items-center justify-between border-b border-zinc-200 pb-4 dark:border-zinc-800">
        <div className="flex flex-col">
          <span className="text-sm font-medium text-black dark:text-zinc-50">
            {me.user.name || me.user.email}
          </span>
          <span className="text-xs text-zinc-500 dark:text-zinc-400">
            {me.user.email}
          </span>
        </div>
        <LogoutButton />
      </header>

      {household ? (
        <section className="flex flex-col gap-4">
          <h1 className="text-xl font-semibold text-black dark:text-zinc-50">
            {household.name}
          </h1>
          <ul className="flex flex-col gap-2">
            {household.members.map((member) => (
              <li
                key={member.user_id}
                className="flex items-center justify-between rounded-md border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-800"
              >
                <span>{member.name || member.email}</span>
                <span className="text-xs text-zinc-500 dark:text-zinc-400">
                  {member.partner_label === "PARTNER_A" ? "Partner A" : "Partner B"} ·{" "}
                  {member.role === "OWNER" ? "Owner" : "Member"}
                </span>
              </li>
            ))}
          </ul>
          {canInvite && <InvitePanel />}
        </section>
      ) : (
        <section className="flex flex-1 flex-col items-center justify-center">
          <CreateHouseholdForm />
        </section>
      )}
    </main>
  );
}
