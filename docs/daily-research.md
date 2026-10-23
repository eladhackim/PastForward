# Daily research (runs unattended once a day)

Each day a scheduled run does three things:
- it starts from this week's news and finds the history it rhymes with;
- it adds a few verified echoes to PastForward, deepest past first;
- on Mondays and Thursdays, it also looks for one new rhyme.

Each run is kept small on purpose:
- at most 2 news stories a run, each giving one echo or one watch-list entry;
- 3 rhymes a run, at most 2 new echoes each;
- at most 1 new rhyme, and only on Mondays and Thursdays;
- about 40 web searches, or about 70 on a new-rhyme day.

Over a 16-day cycle every rhyme is researched again.

## Steps (from the repo root)

1. `git pull` to start from the latest main.
2. `python3 tools/daily_pick.py`. It picks today's 3 rhymes, writes `/tmp/pastforward-daily/input.json` and `rhymes.txt` (every rhyme and the coverage gaps), and says whether today is a new-rhyme day.
3. **From the news.** Follow `docs/news-spec.md`:
   - pick at most 2 of the week's big stories;
   - find the existing rhyme each one echoes, or trace a new pattern back to its seed for the watch list;
   - write `/tmp/pastforward-daily/news.json` and run `python3 tools/news_add.py /tmp/pastforward-daily/news.json`.

   Log a story even when it fits nothing (outcome `none`), so later runs skip it.
4. **Echoes.** Research today's 3 rhymes by the rules in `docs/deep-echo-spec.md`:
   - deep past first;
   - verify every fact with web search;
   - add at most 2 echoes per rhyme, and an empty list is fine.

   Write the result to `/tmp/pastforward-daily/new.json`, keyed by every chosen id (`[]` when nothing passes the bar). Then run `python3 tools/daily_add.py /tmp/pastforward-daily/new.json`. Fix anything it reports, or drop that echo.
5. **New rhyme (new-rhyme days only).** Start from the watch list (`python3 tools/news_add.py --recent`): a rhyme whose Today is in the news is the best kind. Then follow `docs/new-rhyme-spec.md`. Afterwards, close the watch story you used or rejected, through `closed` in a news.json run of `tools/news_add.py`. If you find a rhyme as strong as the best in the app, write `/tmp/pastforward-daily/rhyme.json` and run `python3 tools/rhyme_add.py /tmp/pastforward-daily/rhyme.json`. Fix anything it reports. If a problem cannot be fixed honestly, add no rhyme today. Adding none is a normal outcome.
6. `python3 tools/build.py`. The last lines must say `checks passed`. If not, run `git checkout -- . && git clean -fd data/ r/` and stop without pushing.
7. `python3 tools/og.py` refreshes the share images. It is required on a day a rhyme was added, because every rhyme needs its image. If it fails on such a day, undo as in step 6 and stop. On other days, skip it if it fails.
8. Commit everything. Use the message `Daily research YYYY-MM-DD: +N echoes (<ids>)`. Add `, news: <story> -> <id or watch>` for each news story, and `, new rhyme <id>` when one was added. Push to `main`. Cloudflare publishes it automatically within a minute.
9. Finish with a short summary:
   - the news stories reviewed and what each became (echo of which rhyme, watch with its seed, or none);
   - what was added: year and short name per echo, and the new rhyme as Then → Today → Next;
   - anything you were unsure about.

## Never

- Never edit the original data files: `data/pairs-A…D`, `world-A…D`, `world-now`, `headlines-1…3`, `opportunities-A…D`, `echoes-A…D` and `echoes-2*`/`echoes-3*`, or `map.json`.
- Never edit anything in `functions/` or `src/`, or any setting or secret. `tools/build.py` regenerates `functions/api/_rhymes.js` itself; that is expected.
- New data goes only through `tools/daily_add.py`, `tools/news_add.py` and `tools/rhyme_add.py`, which write the `*-daily` files, `research-log.json` and `news-log.json`.
- Never delete or rewrite existing echoes or rhymes. Report a doubtful one in the summary instead.
- Never push if the build fails, and never use force push.
