import type { NextConfig } from "next";

import { API_URL } from "./src/lib/api-url";

const nextConfig: NextConfig = {
  output: "standalone",
  // Proxies the backend through this app's own origin so cookies the API
  // sets (OAuth state, session) are scoped to this host instead of the
  // API's — see docs/phase1-setup.md "Production cookie domain" for why a
  // split-host deployment otherwise loses the session cookie between the
  // OAuth callback and the dashboard.
  async rewrites() {
    return [{ source: "/api/v1/:path*", destination: `${API_URL}/api/v1/:path*` }];
  },
};

export default nextConfig;
