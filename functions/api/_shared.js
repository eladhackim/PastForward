// Shared helpers for the PastForward API (Cloudflare Pages Functions + D1 bound as env.DB).
export const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
export const RHYME = /^[a-z0-9_-]{1,40}$/;

export function json(data, status = 200, maxAge = 0) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": maxAge ? `public, max-age=${maxAge}, s-maxage=${maxAge}` : "no-store"
    }
  });
}

// Writes only from our own pages (pastforward.app, its Pages previews, or local development).
export function allowedOrigin(request) {
  const o = request.headers.get("Origin");
  if (!o) return true;
  try {
    const h = new URL(o).hostname;
    return h === "pastforward.app" || h.endsWith(".pastforward.app") || h.endsWith(".pages.dev") || h === "localhost" || h === "127.0.0.1";
  } catch (_) { return false; }
}

export async function readJSON(request) {
  try { return await request.json(); } catch (_) { return null; }
}

// Reject if `promise` has not settled within `ms`. A stalled Cache API or D1 call otherwise holds the
// request open until Cloudflare's gateway gives up and answers 504.
export function withTimeout(promise, ms, label) {
  let timer;
  const late = new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(`${label} timed out after ${ms} ms`)), ms); });
  return Promise.race([promise, late]).finally(() => clearTimeout(timer));
}
const CACHE_MS = 1000, BUILD_MS = 3000;

// Serve a GET from Cloudflare's edge cache for `seconds`, so a traffic spike does not hit the database.
// Fail-fast: a slow or failing cache lookup is skipped, and if `build` (the D1 query) is slow or throws,
// `fallback()` is returned instead (never stored in the edge cache). Without a fallback the error is
// rethrown, and _middleware.js turns it into a 500 JSON.
export async function cached(context, seconds, build, fallback) {
  const cache = caches.default;
  const key = new Request(new URL(context.request.url).toString(), { method: "GET" });
  try {
    const hit = await withTimeout(cache.match(key), CACHE_MS, "cache lookup");
    if (hit) return hit;
  } catch (err) {
    console.error("cached: lookup skipped:", String((err && err.message) || err).slice(0, 200));
  }
  let res;
  try {
    res = await withTimeout(build(), BUILD_MS, "database query");
  } catch (err) {
    if (!fallback) throw err;
    console.error("cached: serving fallback:", new URL(context.request.url).pathname, String((err && err.message) || err).slice(0, 200));
    const fb = fallback();
    fb.headers.set("X-PastForward-Fallback", "1");   // tells a fallback apart from real, empty data
    return fb;
  }
  if (res.status === 200) context.waitUntil(cache.put(key, res.clone()).catch(() => {}));
  return res;
}
