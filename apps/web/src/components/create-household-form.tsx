"use client";

import { useActionState } from "react";

import {
  createHouseholdAction,
  type CreateHouseholdState,
} from "@/app/dashboard/actions";
import { Button } from "@/components/ui/button";

const INITIAL: CreateHouseholdState = {};

export function CreateHouseholdForm() {
  const [state, action, pending] = useActionState(createHouseholdAction, INITIAL);

  return (
    <form
      action={action}
      className="flex w-full max-w-sm flex-col gap-3 rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950"
    >
      <h2 className="text-lg font-medium text-black dark:text-zinc-50">
        Create your household
      </h2>
      <label htmlFor="name" className="text-sm text-zinc-600 dark:text-zinc-400">
        Household name
      </label>
      <input
        id="name"
        name="name"
        required
        maxLength={255}
        autoComplete="off"
        className="rounded-md border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-zinc-500 dark:border-zinc-700 dark:bg-zinc-900"
      />
      {state.error && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {state.error}
        </p>
      )}
      <Button type="submit" disabled={pending}>
        {pending ? "Creating…" : "Create household"}
      </Button>
    </form>
  );
}
