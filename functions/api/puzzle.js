// POST /api/puzzle  { day, device, score: 0..3 } → 204   (first result per device per day counts)
// GET  /api/puzzle?day=N → { day, players, perfect }    (cached at the edge for 60 s)
import { json, allowedOrigin, readJSON, cached, UUID } from "./_shared.js";

export async function onRequestPost({ request, env }) {
  if (!allowedOrigin(request)) return json({ error: "origin not allowed" }, 403);
  const b = await readJSON(request);
  const ok = b && Number.isInteger(b.day) && b.day >= 1 && b.day <= 100000 &&
    UUID.test(String(b.device)) && Number.isInteger(b.score) && b.score >= 0 && b.score <= 3;
  if (!ok) return json({ error: "expected { day, device, score: 0..3 }" }, 400);
  await env.DB
    .prepare("INSERT OR IGNORE INTO puzzle_results (day, device_id, score) VALUES (?1, ?2, ?3)")
    .bind(b.day, b.device.toLowerCase(), b.score)
    .run();
  return new Response(null, { status: 204 });
}

export async function onRequestGet(context) {
  const day = Number(new URL(context.request.url).searchParams.get("day"));
  if (!Number.isInteger(day) || day < 1 || day > 100000) return json({ error: "expected ?day=N" }, 400);
  return cached(context, 60, async () => {
    const row = await context.env.DB
      .prepare("SELECT COUNT(*) AS players, COALESCE(SUM(score = 3), 0) AS perfect FROM puzzle_results WHERE day = ?1")
      .bind(day)
      .first();
    return json({ day, players: row.players, perfect: row.perfect }, 200, 60);
  });
}
