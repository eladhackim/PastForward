# PastForward: infrastructure setup brief

You are setting up hosting, a small database and analytics for **PastForward**, a static website at **pastforward.app**. Please do the tasks below, run the checks, and return the values listed at the end. Do not change the site's code.

## What exists today

- **Site:** one static file, `index.html` (no build step, no framework), plus a `CNAME` file. It lives in the GitHub repository **eladhackim/pastforward**, on branch **main**, at the root.
- **Domain:** **pastforward.app**, registered at **Porkbun**. DNS currently points at GitHub Pages: four A records to 185.199.108–111.153 and `www` as a CNAME to eladhackim.github.io.
- **Database script:** `supabase-setup.sql` (attached). It creates two tables (`votes`, `puzzle_results`), two functions (`cast_vote`, `submit_puzzle`) and two read-only summary views (`rhyme_scores`, `puzzle_stats`). The public site can only call the functions and read the views.

## 1. Cloudflare: hosting and DNS

1. Create a Cloudflare account (free plan) and add the site **pastforward.app**.
2. At **Porkbun**, turn off DNSSEC for pastforward.app if it is on. Then replace Porkbun's nameservers with the two Cloudflare nameservers. Wait until Cloudflare shows the zone as **Active**.
3. In Cloudflare, go to **Workers & Pages → Create → Pages → Connect to Git**, and choose the GitHub repository **eladhackim/pastforward**.
   - Project name: `pastforward`
   - Production branch: `main`
   - Framework preset: **None**
   - Build command: *(leave empty)*
   - Build output directory: `/`
4. In the Pages project, under **Custom domains**, add **pastforward.app** and **www.pastforward.app**. Let Cloudflare create the DNS records. Delete the old GitHub Pages A records and the `www` CNAME if they remain.
5. Redirect **www.pastforward.app → https://pastforward.app** with a 301 Redirect Rule, keeping the path and query.
6. Under **SSL/TLS**, set the mode to **Full (strict)** and turn on **Always Use HTTPS**. The .app domain requires HTTPS.
7. Under **Speed**, keep **Rocket Loader off**. It rewrites inline scripts and can break the page.
8. Optional: turn on **Web Analytics** for the Pages project. It's free and cookie-free.
9. Once https://pastforward.app loads from Cloudflare, go to the GitHub repository's **Settings → Pages** and turn GitHub Pages **off**.

**Check:** https://pastforward.app and https://www.pastforward.app both load the site over HTTPS, and www redirects to the bare domain. A new commit to `main` redeploys automatically.

## 2. Supabase: votes and puzzle stats

1. Create a Supabase account and a project named **pastforward** in the **EU Central (Frankfurt)** region. The free plan is fine for now. Note: free projects pause after a week with no traffic, so upgrade to **Pro** before the public launch.
2. Open **SQL Editor → New query**, paste all of `supabase-setup.sql`, and press **Run**. It must finish with no errors.
3. Do **not** turn on any Auth providers, Storage buckets or extra tables. They aren't needed.
4. In **Project Settings → API**, copy the **Project URL** and the **publishable key**. On older projects this is the **anon public key**. Never share the secret or service_role key; it isn't needed.

**Checks**, run with the publishable or anon key (`KEY`) and the project URL (`URL`):

```bash
# a. cast a test vote (expect HTTP 200 or 204)
curl -i -X POST "$URL/rest/v1/rpc/cast_vote" \
  -H "apikey: $KEY" -H "Content-Type: application/json" \
  -d '{"p_rhyme":"flu","p_device":"00000000-0000-4000-8000-000000000001","p_vote":1}'

# b. read the summary (expect [{"rhyme_id":"flu","yes":1,"no":0}])
curl -s "$URL/rest/v1/rhyme_scores?select=*" -H "apikey: $KEY"

# c. the raw table must NOT be readable (expect an error or permission denied, not rows)
curl -s "$URL/rest/v1/votes?select=*" -H "apikey: $KEY"

# d. puzzle: submit and read (expect players 1)
curl -i -X POST "$URL/rest/v1/rpc/submit_puzzle" \
  -H "apikey: $KEY" -H "Content-Type: application/json" \
  -d '{"p_day":1,"p_device":"00000000-0000-4000-8000-000000000001","p_score":3}'
curl -s "$URL/rest/v1/puzzle_stats?day=eq.1&select=*" -H "apikey: $KEY"
```

If an older project rejects the requests, add `-H "Authorization: Bearer $KEY"` when KEY is the legacy anon key (it starts with `eyJ`).

Then remove the test data in the SQL Editor:

```sql
delete from public.votes where device_id = '00000000-0000-4000-8000-000000000001';
delete from public.puzzle_results where device_id = '00000000-0000-4000-8000-000000000001';
```

## 3. PostHog: product analytics

1. Create a PostHog account on **EU Cloud** (eu.posthog.com) and a project named **PastForward**.
2. Turn off **session recording** and **autocapture of heatmaps** in project settings. We will send a small set of named events only.
3. Copy the **Project API key** (starts with `phc_`).

## 4. GitHub access (Elad does this, not the agent)

Give the Claude GitHub app access to **eladhackim/pastforward** at https://github.com/apps/claude/installations/select_target, so Claude can push site updates.

## Return these values

| # | What | Example |
|---|------|---------|
| 1 | Supabase Project URL | `https://abcd1234.supabase.co` |
| 2 | Supabase publishable key, or legacy anon public key | `sb_publishable_…` or `eyJ…` |
| 3 | Results of checks a–d (pasted output) | |
| 4 | PostHog Project API key and region | `phc_…`, EU |
| 5 | Cloudflare Pages URL and confirmation that https://pastforward.app is served by Cloudflare | `pastforward.pages.dev` |
| 6 | Any setting you could not apply as written | |

The Supabase publishable key and the PostHog project key are designed to be public; they will be placed in the website code. **Do not** send any secret or service_role key, passwords or recovery codes.
