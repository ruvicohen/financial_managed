import { afterEach, describe, expect, it, vi } from "vitest";

import { getHealth } from "./api";

describe("getHealth", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns the parsed status on a successful response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok" }),
      }),
    );

    await expect(getHealth()).resolves.toEqual({ status: "ok" });
  });

  it("returns null when the backend is unreachable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("network error")),
    );

    await expect(getHealth()).resolves.toBeNull();
  });
});
