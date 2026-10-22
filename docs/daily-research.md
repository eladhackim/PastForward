# Daily echo research (runs unattended once a day)

Each day a scheduled run adds a few verified echoes to PastForward, deepest past first, and publishes them. It is kept small on purpose: 3 rhymes a run, at most 2 new echoes per rhyme, and about 30 web searches in total. Over a 16-day cycle every rhyme gets researched again.

## Steps (from the repo root)

1. `git pull` to start from the latest main.
2. `python3 tools/daily_pick.py` picks today's 3 rhymes and writes `/tmp/pastforward-daily/input.json`.
3. Research those rhymes by the rules in `docs/deep-echo-spec.md` (deep past first; verify every fact with web search; an empty list is fine). Add at most 2 echoes per rhyme. Write the result to `/tmp/pastforward-daily/new.json`, keyed by every chosen id (`[]` when nothing passes the bar).
4. `python3 tools/daily_add.py /tmp/pastforward-daily/new.json`. If it reports errors, fix them and run it again. If an echo cannot be fixed, drop it.
5. `python3 tools/build.py`. The last lines must say `checks passed`. If not, run `git checkout -- . && git clean -fd data/` and stop without pushing.
6. If `python3 -c "import playwright"` works, run `python3 tools/og.py` to refresh the share images. If it fails, skip it.
7. Commit everything with the message `Daily echo research YYYY-MM-DD: +N echoes (<ids>)` and push to `main`. Cloudflare publishes it automatically within a minute.
8. Finish with a two-line summary: what was added (year and short name per echo) and anything you were unsure about.

## Never

- Never edit `data/pairs-*`, `world-*`, `headlines-*`, `opportunities-*`, `map.json`, anything in `functions/` or `src/`, or any setting or secret.
- Never delete or rewrite existing echoes. Report a doubtful one in the summary instead.
- Never push if the build fails, and never use force push.
