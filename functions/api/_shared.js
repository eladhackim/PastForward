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

// Serve a GET from Cloudflare's edge cache for `seconds`, so a traffic spike does not hit the database.
export async function cached(context, seconds, build) {
  const cache = caches.default;
  const key = new Request(new URL(context.request.url).toString(), { method: "GET" });
  const hit = await cache.match(key);
  if (hit) return hit;
  const res = await build();
  if (res.status === 200) context.waitUntil(cache.put(key, res.clone()));
  return res;
}
