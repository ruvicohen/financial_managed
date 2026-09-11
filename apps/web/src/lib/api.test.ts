import { afterEach, describe, expect, it, vi } from "vitest";

import { getHealth, getMe } from "./api";

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

describe("getMe", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns the parsed session on 200", async () => {
    const body = {
      user: { id: "u1", email: "a@example.com", name: "A", picture_url: null },
      household: null,
    };
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => body });
    vi.stubGlobal("fetch", fetchMock);

    await expect(getMe("fm_session=abc")).resolves.toEqual(body);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/auth/me"),
      expect.objectContaining({ headers: { cookie: "fm_session=abc" } }),
    );
  });

  it("returns null on 401", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 401 }));
    await expect(getMe("")).resolves.toBeNull();
  });
});
