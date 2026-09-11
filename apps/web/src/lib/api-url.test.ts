import { afterEach, describe, expect, it, vi } from "vitest";

// Regression: Render's blueprint `fromService`/`hostport` (render.yaml)
// resolves API_URL to a bare "host:port" with no scheme, e.g.
// "financial-managed-api:8000". Handed straight to fetch/redirect, a browser
// parses the part before ":" as the URL scheme and fails with "the scheme
// does not have a registered handler" instead of reaching the API.
describe("API_URL", () => {
  const original = process.env.API_URL;

  afterEach(async () => {
    if (original === undefined) delete process.env.API_URL;
    else process.env.API_URL = original;
    vi.resetModules();
  });

  it("prepends http:// when the env var has no scheme", async () => {
    process.env.API_URL = "financial-managed-api:8000";
    const { API_URL } = await import("./api-url");
    expect(API_URL).toBe("http://financial-managed-api:8000");
  });

  it("leaves an already-schemed URL untouched", async () => {
    process.env.API_URL = "https://api.example.com";
    const { API_URL } = await import("./api-url");
    expect(API_URL).toBe("https://api.example.com");
  });

  it("falls back to localhost when unset", async () => {
    delete process.env.API_URL;
    const { API_URL } = await import("./api-url");
    expect(API_URL).toBe("http://localhost:8000");
  });
});
