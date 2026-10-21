// POST /api/ask/status { key } → { ok, plan, left, limit, resets }   (checks a licence; never calls the model)
import { json, allowedOrigin, readJSON } from "../_shared.js";
import { askConfig, ensureTables, checkLicence, KEY_RE, usedThisMonth, nextMonthStart } from "../_ask.js";

export async function onRequestPost({ request, env }) {
  const cfg = askConfig(env);
  if (!cfg.enabled) return json({ error: "paused" }, 503);
  if (!allowedOrigin(request)) return json({ error: "origin not allowed" }, 403);
  const b = await readJSON(request);
  const key = b && typeof b.key === "string" ? b.key.trim() : "";
  if (!KEY_RE.test(key)) return json({ ok: false, reason: "invalid" }, 402);
  await ensureTables(env);
  const lic = await checkLicence(env, key);
  if (!lic.ok) return json({ ok: false, reason: lic.status || "invalid" }, 402);
  const used = await usedThisMonth(env, lic.hash);
  return json({ ok: true, plan: lic.plan || null, left: Math.max(0, cfg.limit - used), limit: cfg.limit, resets: nextMonthStart() });
}
