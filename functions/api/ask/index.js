// POST /api/ask  { key, q } → { answer, left, limit, cached }
// Paid only. See ../_ask.js for the gates every question passes before any money is spent.
import { json, allowedOrigin, readJSON } from "../_shared.js";
import {
  askConfig, ensureTables, checkLicence, KEY_RE, MAX_Q, cleanQuestion, normQuestion, cacheKey,
  cachedAnswer, storeAnswer, usedThisMonth, reserveAllowance, releaseAllowance,
  reserveSpend, settleSpend, reserveMicro, costMicro, callModel, cleanAnswer, nextMonthStart
} from "../_ask.js";

export async function onRequestPost({ request, env }) {
  const cfg = askConfig(env);
  if (!cfg.enabled) return json({ error: "paused" }, 503);
  if (!allowedOrigin(request)) return json({ error: "origin not allowed" }, 403);
  const b = await readJSON(request);
  const key = b && typeof b.key === "string" ? b.key.trim() : "";
  const q = cleanQuestion(b && b.q);
  if (!KEY_RE.test(key)) return json({ error: "licence", reason: "invalid" }, 402);
  if (q.length < 3 || q.length > MAX_Q) return json({ error: "question", max: MAX_Q }, 400);
  await ensureTables(env);

  const lic = await checkLicence(env, key);
  if (!lic.ok) return json({ error: "licence", reason: lic.status || "invalid" }, 402);

  const qn = normQuestion(q);
  const qHash = await cacheKey(qn);
  const hit = await cachedAnswer(env, qHash);
  if (hit) {
    const used = await usedThisMonth(env, lic.hash);
    return json({ answer: hit, cached: true, left: Math.max(0, cfg.limit - used), limit: cfg.limit });
  }

  const al = await reserveAllowance(env, lic.hash, cfg.limit);
  if (!al.ok) return json({ error: "allowance", left: 0, limit: cfg.limit, resets: nextMonthStart() }, 429);

  const reserved = reserveMicro(cfg, q);
  const sp = await reserveSpend(env, cfg, reserved);
  if (!sp.ok) {
    await releaseAllowance(env, lic.hash, al.month);
    return json({ error: "resting", until: sp.why === "month" ? nextMonthStart() : "tomorrow" }, 503);
  }

  let out;
  try {
    out = await callModel(env, cfg, q);
  } catch (e) {
    console.error("ask model error", String(e && e.message || e).slice(0, 300));
    await releaseAllowance(env, lic.hash, al.month);
    // A refused or failed request is not billed; a timeout might be, so keep that reservation.
    if (e && e.charged === false) await settleSpend(env, sp.day, -reserved, -1);
    return json({ error: "model" }, 502);
  }
  const actual = costMicro(cfg, out.usage);
  await settleSpend(env, sp.day, actual - reserved);
  console.log("ask", JSON.stringify({ micro: actual, in: out.usage.input_tokens, out: out.usage.output_tokens, stop: out.stop }));

  const answer = cleanAnswer(out.input);
  if (!answer) {
    await releaseAllowance(env, lic.hash, al.month);
    return json({ error: "model" }, 502);
  }
  if (answer.on_topic) await storeAnswer(env, qHash, q, answer);
  return json({ answer, cached: false, left: Math.max(0, cfg.limit - al.used), limit: cfg.limit });
}
