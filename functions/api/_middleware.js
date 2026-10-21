// Runs before every /api handler: a clear JSON error instead of a crash page (Cloudflare 1101).
export async function onRequest(context) {
  if (!context.env.DB) {
    return new Response(JSON.stringify({ error: "database not bound: add D1 binding DB and redeploy" }), {
      status: 503, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" }
    });
  }
  try {
    return await context.next();
  } catch (err) {
    const msg = String((err && err.message) || err).slice(0, 200);
    console.error("api error", context.request.method, new URL(context.request.url).pathname, msg);
    const hint = /no such table/i.test(msg) ? "tables missing: run d1-schema.sql in the D1 console" : "server error";
    return new Response(JSON.stringify({ error: hint }), {
      status: 500, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" }
    });
  }
}
