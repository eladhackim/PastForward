# Daily research (runs unattended once a day)

Each day a scheduled run adds a few verified echoes to PastForward, deepest past first. On Mondays and Thursdays it also looks for one new rhyme. Each run is kept small on purpose:
- 3 rhymes a run, at most 2 new echoes each;
- at most 1 new rhyme, and only on Mondays and Thursdays;
- about 30 web searches, or about 60 on a new-rhyme day.

Over a 16-day cycle every rhyme is researched again.

## Steps (from the repo root)

1. `git pull` to start from the latest main.
2. `python3 tools/daily_pick.py`. It picks today's 3 rhymes, writes `/tmp/pastforward-daily/input.json` and `rhymes.txt` (every rhyme and the coverage gaps), and says whether today is a new-rhyme day.
3. **Echoes.** Research today's 3 rhymes by the rules in `docs/deep-echo-spec.md`:
   - deep past first;
   - verify every fact with web search;
   - add at most 2 echoes per rhyme, and an empty list is fine.

   Write the result to `/tmp/pastforward-daily/new.json`, keyed by every chosen id (`[]` when nothing passes the bar). Then run `python3 tools/daily_add.py /tmp/pastforward-daily/new.json`. Fix anything it reports, or drop that echo.
4. **New rhyme (new-rhyme days only).** Follow `docs/new-rhyme-spec.md`. If you find a rhyme as strong as the best in the app, write `/tmp/pastforward-daily/rhyme.json` and run `python3 tools/rhyme_add.py /tmp/pastforward-daily/rhyme.json`. Fix anything it reports. If a problem cannot be fixed honestly, add no rhyme today. Adding none is a normal outcome.
5. `python3 tools/build.py`. The last lines must say `checks passed`. If not, run `git checkout -- . && git clean -fd data/ r/` and stop without pushing.
6. `python3 tools/og.py` refreshes the share images. It is required on a day a rhyme was added, because every rhyme needs its image. If it fails on such a day, undo as in step 5 and stop. On other days, skip it if it fails.
7. Commit everything. Use the message `Daily research YYYY-MM-DD: +N echoes (<ids>)`, adding `, new rhyme <id>` when one was added. Push to `main`. Cloudflare publishes it automatically within a minute.
8. Finish with a short summary:
   - what was added: year and short name per echo, and the new rhyme as Then → Today → Next;
   - anything you were unsure about.

## Never

- Never edit the original data files: `data/pairs-A…D`, `world-A…D`, `world-now`, `headlines-1…3`, `opportunities-A…D`, `echoes-A…D` and `echoes-2*`/`echoes-3*`, or `map.json`.
- Never edit anything in `functions/` or `src/`, or any setting or secret. `tools/build.py` regenerates `functions/api/_rhymes.js` itself; that is expected.
- New data goes only through `tools/daily_add.py` and `tools/rhyme_add.py`, which write the `*-daily` files and `research-log.json`.
- Never delete or rewrite existing echoes or rhymes. Report a doubtful one in the summary instead.
- Never push if the build fails, and never use force push.
