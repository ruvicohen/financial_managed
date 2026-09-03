import { expect, test } from "@playwright/test";

// Not run in CI yet (Phase 0 defers real E2E infrastructure). Run locally with
// `pnpm exec playwright test` against a running dev server.
test.skip("home page loads", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Financial Managed" })).toBeVisible();
});
