// GET /api/ask/config → { enabled, limit, monthly, yearly, portal, priceMonthly, priceYearly }   (public; cached 5 minutes)
import { json } from "../_shared.js";
import { askConfig } from "../_ask.js";

const txt = (v, d) => (typeof v === "string" && /^[^<>"]{1,12}$/.test(v.trim()) ? v.trim() : d);
const url = v => (typeof v === "string" && /^https:\/\/[^\s"<>]+$/.test(v) ? v : null);
export async function onRequestGet({ env }) {
  const cfg = askConfig(env);
  return json({
    enabled: cfg.enabled, limit: cfg.limit,
    monthly: url(env.LS_CHECKOUT_MONTHLY), yearly: url(env.LS_CHECKOUT_YEARLY), portal: url(env.LS_PORTAL),
    priceMonthly: txt(env.LS_PRICE_MONTHLY, "€3"), priceYearly: txt(env.LS_PRICE_YEARLY, "€19")
  }, 200, 300);
}
