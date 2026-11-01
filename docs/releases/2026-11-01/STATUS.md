# PastForward — 1 November 2026

Owner explicitly chose **Hold live AI/payment tests; keep current deployment**. No provider migration, live AI request, payment, or deployment is authorized by that choice. Continue non-paid validation; do not claim the blocked release gates passed.

- Worktree baseline: `f531301797d60bf6a384123dcaf1ce463c091266`. Previous source commit: `b9e7e89`; Cloudflare deployment rollback identifier still needs read-only verification before any future deployment.
- No seventh new artifact supplied; use the repository's current approved design as the baseline.
- Python build passed: 50 rhymes, 380 echoes, 62 world years. Generated index identical to committed output.
- Echo validation passed with historical-date warnings; 192 guides validated without issues.
- Isolated local Playwright rendering passed at 390 and 1440 pixels: home, full story, Your future, daily; no JS errors or overflow. API responses were stubbed in this local UI check, so it does not prove live AI/payment flows.
- Live browser check returned HTTP 200 and exact candidate HTML SHA-256 `d43c42d817e69687f411484d817c6ba3c128952f571c61de86ba23ce481ba68f`. Evidence `/tmp/pastforward-live-verification.json`.
- Public read-only live API checks: scores, daily puzzle, Ask config returned 200. Ask is enabled with limit 30 and checkout links present. No inference or checkout invoked.
- Current Ask server implementation uses Anthropic, per-license allowance and atomic budget reservations. Owner's Anthropic-credit restriction remains in force; public config checks are not cost-protection acceptance tests.
- Current deployment retained. This is verification evidence, not a newly shipped release.

## New forecast feature authorized after the deployment hold

Owner requested predictions front and center and chose **Evidence-based scenarios by year, with sources and signals to watch; add AI later**. The new candidate is static and does not call AI or payment endpoints. Current production remains unchanged; live Ask/payment acceptance is still held.

- Home now leads with “What comes next?”, year shortcuts and scenario previews. Existing historical river, full stories, daily puzzle and personal lifeline remain accessible.
- Six dated scenarios cover 2026–2030 using verified IMF October 2026, IEA February/July 2026 and WMO May 2026 projections. Each separates source projection from editorial interpretation and includes signals, supporting/weakening conditions, limits and a historical context link.
- Multi-year windows retain their source meaning: selecting 2027 does not turn an 86% five-year probability into an annual probability. No invented probabilities or calendar-gap forecasts.
- Data lives in `data/forecasts.json`; build validates sources, dates, windows, signals and rhyme references before writing output. Review due January 1, 2027; stale content is labelled, and dates never silently roll forward.
- Build and eight catalog validation tests passed. Browser smoke passed at 320, 390 and 1440 px, both themes: every year, sources, topic empty state/recovery, details, historical lifeline, Back/Escape, existing full story, and 2031 stale-date behavior. No JS errors or AI/payment requests. Evidence: `/tmp/pastforward-outlook-smoke/results.json`.
- Local preview: `http://127.0.0.1:4183/`. Publication and live paid-flow testing have not occurred.

Reproduce: `PYTHONDONTWRITEBYTECODE=1 python3 tools/build.py`; `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p 'test_*.py'`. Serve the root locally, then run `node tools/smoke_outlook.cjs` with Playwright available (or set `PLAYWRIGHT_MODULE` to an installed module path). Set `PASTFORWARD_TEST_URL` for another local port. The browser harness stubs API responses and is not live backend acceptance.
