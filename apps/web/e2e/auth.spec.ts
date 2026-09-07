import { expect, test } from "@playwright/test";

// Not run in CI yet (E2E infrastructure is deferred). Run locally against a
// running dev server: `pnpm --filter web exec playwright test`.

test("unauthenticated visit to /dashboard redirects to /login", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login$/);
  await expect(
    page.getByRole("link", { name: "Sign in with Google" }),
  ).toBeVisible();
});

test("login page shows the not-authorized notice", async ({ page }) => {
  await page.goto("/login?error=not_authorized");
  await expect(page.getByRole("alert")).toContainText("isn't authorized");
});
