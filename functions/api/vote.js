// POST /api/vote  { rhyme, device, vote: 1 | -1 } → 204. One vote per device per rhyme; a device can change its vote.
import { json, allowedOrigin, readJSON, UUID, RHYME } from "./_shared.js";

export async function onRequestPost({ request, env }) {
  if (!allowedOrigin(request)) return json({ error: "origin not allowed" }, 403);
  const b = await readJSON(request);
  if (!b || !RHYME.test(String(b.rhyme)) || !UUID.test(String(b.device)) || ![1, -1].includes(b.vote)) {
    return json({ error: "expected { rhyme, device, vote: 1 | -1 }" }, 400);
  }
  await env.DB
    .prepare(`INSERT INTO votes (rhyme_id, device_id, vote) VALUES (?1, ?2, ?3)
              ON CONFLICT (rhyme_id, device_id) DO UPDATE SET vote = excluded.vote, created_at = datetime('now')`)
    .bind(b.rhyme, b.device.toLowerCase(), b.vote)
    .run();
  return new Response(null, { status: 204 });
}
