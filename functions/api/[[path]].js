// Catch-all for /api/* paths with no handler of their own (/api/foo, /api/.env, or a real route called
// with the wrong method). Without it they fall through to the static site and return index.html with 200.
// Pages picks the more specific route files first, so real handlers never reach this. No database use.
import { json } from "./_shared.js";

export function onRequest() {
  return json({ error: "not found" }, 404);
}
