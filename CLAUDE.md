# PastForward — CLAUDE.md

Deploy runbook for operating this repo from Claude Code on Elad's Mac. Anything marked **unverified** is not confirmed by a file in this repo; check it before relying on it.

## Deploy runbook

### 1. What the app is

PastForward ("History rhymes") is a static site with a small API. Live at **https://pastforward.app** (`CNAME`).

- **Site:** one generated static file, `index.html`, plus share pages `r/*.html`, icons, `sitemap.xml`, `robots.txt`, `site.webmanifest`. No framework and no `package.json`.
- **Source:** `src/template.html` (markup, styles, code) + `data/*.json` (content). `tools/build.py` merges them.
- **API:** Cloudflare Pages Functions in `functions/api/` (`_routes.json` sends only `/api/*` to Functions).
- **Database:** Cloudflare D1, bound to the Pages project as `DB`. Database name `pastforward` (from `docs/SETUP-UPDATE.md` and `d1-schema.sql`); the database id is not in the repo.
- **Hosting:** Cloudflare Pages project `pastforward`, account `758ea389f3b7be91b7d161a3ecb5d35b`, connected to GitHub `eladhackim/PastForward`, production branch `main`.
- **Ask PastForward** (paid feature, `functions/api/_ask.js`): calls the Anthropic API and checks Lemon Squeezy licences. It costs real money per question.
- No `wrangler.toml`, no GitHub Actions workflows, no mobile apps.

Generated files — never edit by hand, rebuild instead: `index.html`, `r/*.html`, `favicon*.svg`, `site.webmanifest`, `robots.txt`, `sitemap.xml`, `functions/api/_rhymes.js`.

### 2. One-time setup on the Mac

```bash
gh auth login            # GitHub: push to main, open and merge PRs
npx wrangler login       # Cloudflare; pick account 758ea389f3b7be91b7d161a3ecb5d35b
npx wrangler whoami      # confirm the account
```

- Python 3 is needed for the build (`python3 tools/build.py`). `tools/og.py` (share images) may need extra Python packages: **unverified**, read its header before running.
- Node is needed only for `tools/grid.mjs` (map, rarely) and `tools/smoke_outlook.cjs` (needs Playwright).
- Wrangler is optional here: the normal deploy is a git push. It is used only for read-only checks and rollback lookups. The repo has no wrangler config, so every `wrangler` command in this file is **unverified** against this repo.

Secrets and variables live only in Cloudflare: Workers & Pages → `pastforward` → Settings → Variables and Secrets (Production). Names, from `docs/SETUP-ASK.md`:

| Name | Type | Where it comes from |
|---|---|---|
| `ANTHROPIC_API_KEY` | Secret | Claude Console |
| `ASK_OWNER_KEY` | Secret | Elad's own test key; random string he generates |
| `LS_STORE_ID`, `LS_PRODUCT_ID`, `LS_CHECKOUT_MONTHLY`, `LS_CHECKOUT_YEARLY`, `LS_PORTAL` | Text | Lemon Squeezy dashboard |
| `ASK_ENABLED` | Text | `1` turns Ask on, `0` pauses it |
| `ASK_CAP_MONTH_USD`, `ASK_CAP_DAY_USD`, `ASK_MONTHLY`, `ASK_MODEL`, `LS_PRICE_MONTHLY`, `LS_PRICE_YEARLY` | Text, optional | Defaults are in `functions/api/_ask.js` |

Variable changes apply only to new deployments: after saving, Deployments → latest production deployment → Retry deployment.

### 3. Build and test

Run from the repo root.

```bash
python3 tools/build.py                                    # validates data, writes index.html and the other generated files; must end with "checks passed"
python3 -m unittest discover -s tools -p 'test_*.py'      # forecast catalog tests
python3 tools/check_echoes.py data/echoes-<name>.json     # optional, per file
python3 tools/check_guides.py data/guides-A.json          # optional, per file
python3 tools/og.py                                       # refresh share images; required when a rhyme was added
```

Prefix with `PYTHONDONTWRITEBYTECODE=1` to avoid creating `tools/__pycache__`.

Browser smoke test (stubs the API, so it does not test the live backend):

```bash
python3 -m http.server 4183          # unverified: the repo says "serve the root locally" but names no command
node tools/smoke_outlook.cjs         # default URL http://127.0.0.1:4183/; override with PASTFORWARD_TEST_URL, PLAYWRIGHT_MODULE
```

Map regeneration (rare): see `README.md`.

If the build fails after content changes, undo with `git checkout -- . && git clean -fd data/ r/` (from `docs/daily-research.md`).

### 4. Deploy

**Site and API (the only documented path): push to `main`.** Cloudflare Pages deploys automatically; the project has no build command and the output directory is `/`, so the committed `index.html` is what ships. Always build and commit before pushing.

```bash
git pull
python3 tools/build.py                                   # must end with "checks passed"
python3 -m unittest discover -s tools -p 'test_*.py'
git status                                               # generated files must be committed with the source change
git push origin main                                     # or merge a PR: gh pr merge <number> --merge
```

Confirm the deployment landed:

```bash
gh api repos/eladhackim/PastForward/commits/main/check-runs --jq '.check_runs[] | {name, status, conclusion}'   # Cloudflare Pages check
npx wrangler pages deployment list --project-name pastforward                                                   # unverified
```

- **Manual deploy** (`npx wrangler pages deploy . --project-name pastforward`): **unverified** and not documented in this repo. Do not use it unless Elad asks; it would upload the whole working tree, not a commit.
- **`--keep-vars`:** this repo has no Cloudflare Worker, so there is no `wrangler deploy`. If a Worker is ever added, deploy it with `npx wrangler deploy --keep-vars` so existing vars and secrets are not cleared.
- **Redeploy without a code change** (after a variable or binding change): dashboard → Deployments → latest production deployment → Retry deployment.

**D1 schema.** There are no migrations. `d1-schema.sql` was run once in Cloudflare → Workers & Pages → D1 → `pastforward` → Console; every statement is `CREATE TABLE IF NOT EXISTS`. The Ask tables create themselves on first use. To apply a schema change, paste the new statements in the same console. CLI alternative, **unverified**:

```bash
npx wrangler d1 list                                                      # read-only: confirm name and id first
npx wrangler d1 execute pastforward --remote --file d1-schema.sql
```

**Daily content run:** follow `docs/daily-research.md`; it ends with a push to `main`.

### 5. Verify live

```bash
curl -sI https://pastforward.app | head -1                 # HTTP 200
curl -s https://pastforward.app/api/scores                 # JSON array of vote totals (cached 60 s)
curl -s "https://pastforward.app/api/puzzle?day=1"         # {"day":1,"players":…,"perfect":…}
curl -s https://pastforward.app/api/ask/config             # Ask config: enabled flag and checkout links
curl -s -o /dev/null -w '%{http_code}\n' https://pastforward.app/api/nope   # 404 for unknown /api routes
```

- Open https://pastforward.app and one share page, e.g. https://pastforward.app/r/bankrun.html.
- To prove the new build is live, compare the page with the committed file: `curl -s https://pastforward.app | shasum -a 256` against `shasum -a 256 index.html`. Cloudflare may inject the Web Analytics beacon, so the hashes can differ: **unverified**; fall back to grepping for a string from the change.
- An API error `database not bound` means the `DB` binding is missing; `tables missing` means `d1-schema.sql` was not run.
- Write checks (`POST /api/vote`, `/api/puzzle`) and their cleanup SQL are in `docs/SETUP-UPDATE.md`. They write test rows to production; ask Elad first.
- Ask checks in `docs/SETUP-ASK.md` section 4. Checks b, c and e need a key, and c spends Anthropic credit: only with Elad's yes.

### 6. Rollback

1. **Dashboard (documented in `docs/releases/2026-11-01/STATUS.md`):** Cloudflare → Workers & Pages → `pastforward` → Deployments → pick the previous production deployment → Rollback to this deployment. Note the current deployment id before each release.
2. **Source fallback:** revert on `main`, which triggers a normal deploy. Never reset or force-push `main`.
   ```bash
   git revert <bad-commit>            # for a merged PR: git revert -m 1 <merge-commit>
   git push origin main
   ```
3. **CLI:** `npx wrangler pages deployment list --project-name pastforward` to find ids. A `wrangler pages` rollback command is **unverified**; use the dashboard.
4. **Ask (spend) stops**, from `docs/SETUP-ASK.md`: instant stop is disabling the API key in the Claude Console; clean stop is `ASK_ENABLED=0` then Retry deployment.
5. **D1:** a Pages rollback does not roll back data or schema. D1 Time Travel restore is a platform feature, **unverified** for this database; do not run a restore without Elad's explicit yes.

### 7. Safety rules

- Live deploys (any push or merge to `main`, Retry deployment, rollback), variable or secret changes, and anything that spends money need Elad's own yes each time. A live Ask question and a Lemon Squeezy checkout both count as spend; so does raising `ASK_CAP_MONTH_USD` or `ASK_CAP_DAY_USD`.
- Never print, log, commit or paste secret values (`ANTHROPIC_API_KEY`, `ASK_OWNER_KEY`, licence keys). Refer to them by name only.
- Do not create, recreate, replace, rename or delete the D1 database `pastforward`, and do not drop tables or bulk-delete rows. Do not change the `DB` binding.
- Do not attach or change custom domains or DNS, and do not buy or upgrade paid services, unless Elad explicitly asks.
- Do not edit generated files by hand; edit `src/template.html` or `data/` and rebuild.
- The daily content run must not touch `functions/`, `src/`, the original data files, or any setting or secret (`docs/daily-research.md`).
- Do not add a `wrangler.toml`, CI workflow or build command to change how the site deploys without Elad's yes.
