# Update to the setup brief: Cloudflare only

We are simplifying the setup. **Do not set up Supabase or PostHog.** Skip sections 2 and 3 of SETUP-BRIEF.md. If you already created either one, delete the project; nothing from it is needed.

Keep **section 1 (Cloudflare hosting and DNS)** exactly as written. Then do the steps below so that votes, puzzle stats and analytics all run on Cloudflare too.

## What changes

| Job | Before | Now |
|-----|--------|-----|
| Hosting | Cloudflare Pages | Cloudflare Pages (unchanged) |
| Votes and puzzle stats | Supabase | **Cloudflare D1** (built-in SQLite database), behind a small API on the same site: `/api/scores`, `/api/vote`, `/api/puzzle` |
| Analytics | PostHog | **Cloudflare Web Analytics** (free, no cookies) |

The API code is a `functions/` folder that Claude adds to the repository. Cloudflare Pages deploys it automatically with the site. You only create the database, connect it, and test.

## 2 (new). Cloudflare D1 database

1. Go to **Workers & Pages → D1 → Create database**. Name it **pastforward**. If a location hint is offered, choose **Western Europe**.
2. Open the database's **Console**, paste all of **d1-schema.sql** (attached), and run it. It creates two tables: `votes` and `puzzle_results`.
3. Open the Pages project **pastforward → Settings → Bindings → Add → D1 database**:
   - Variable name: **`DB`** (exactly this, in capitals)
   - D1 database: **pastforward**
   - Add it for **Production** and for **Preview**.
4. Bindings apply on the next deployment. After the `functions/` folder is in the repository (see below), trigger a redeploy from the Pages dashboard (Deployments → latest → Retry deployment) if one did not run automatically.

## 3 (new). Cloudflare Web Analytics

In the Pages project, open **Metrics → Web Analytics → Enable**. Cloudflare adds its small, cookie-free beacon automatically on the next deploy. Nothing needs to change in the site code.

## Code in the repository (Claude or Elad, not the agent)

Claude adds these files to **eladhackim/pastforward**:

```
functions/api/_shared.js
functions/api/scores.js
functions/api/vote.js
functions/api/puzzle.js
d1-schema.sql
index.html            (updated: now talks to /api)
```

If Claude has no GitHub access yet, Elad uploads them through GitHub's web page (Add file → Upload files, dragging in the `functions` folder keeps its structure).

## Checks (after the database is bound and the functions are deployed)

```bash
D=00000000-0000-4000-8000-000000000001

# a. vote (expect HTTP 204)
curl -i -X POST https://pastforward.app/api/vote \
  -H "Content-Type: application/json" -H "Origin: https://pastforward.app" \
  -d "{\"rhyme\":\"flu\",\"device\":\"$D\",\"vote\":1}"

# b. totals (expect [{"rhyme_id":"flu","yes":1,"no":0}]; may take up to 60 s to refresh, it is cached)
curl -s https://pastforward.app/api/scores

# c. writes from other websites are refused (expect HTTP 403)
curl -i -X POST https://pastforward.app/api/vote \
  -H "Content-Type: application/json" -H "Origin: https://example.com" \
  -d "{\"rhyme\":\"flu\",\"device\":\"$D\",\"vote\":1}"

# d. puzzle (expect 204, then {"day":1,"players":1,"perfect":1})
curl -i -X POST https://pastforward.app/api/puzzle \
  -H "Content-Type: application/json" -H "Origin: https://pastforward.app" \
  -d "{\"day\":1,\"device\":\"$D\",\"score\":3}"
curl -s "https://pastforward.app/api/puzzle?day=1"
```

Then remove the test data in the D1 Console:

```sql
DELETE FROM votes WHERE device_id = '00000000-0000-4000-8000-000000000001';
DELETE FROM puzzle_results WHERE device_id = '00000000-0000-4000-8000-000000000001';
```

## Return these values (replaces the list in SETUP-BRIEF.md)

1. Confirmation that **https://pastforward.app** is served by Cloudflare Pages, with www redirecting to it.
2. The D1 database name and ID, and confirmation that the binding is named **`DB`** for Production and Preview.
3. Confirmation that Web Analytics is enabled.
4. The output of checks a to d.
5. Any setting you could not apply as written.

No keys or secrets are needed from you any more. Do not send passwords or recovery codes.
