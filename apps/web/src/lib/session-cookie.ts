// Must match the API's `session_cookie_name` setting (apps/api/app/config.py,
// env var SESSION_COOKIE_NAME, default "fm_session"). Read from the process
// environment so an operator who overrides it on the API doesn't silently
// break the web app's session check (see proxy.ts) and logout.
export const SESSION_COOKIE_NAME = process.env.SESSION_COOKIE_NAME ?? "fm_session";
