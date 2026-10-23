# From the news: this week's echoes and their seeds

PastForward should feel alive: when someone opens it, they see either a past they know (the Spanish flu) or something from this week's news, with the history it rhymes with. This step starts from the news and works backwards:

1. A big recent story.
2. The pattern it follows.
3. Where it has happened before, back to its **seed**, the oldest real case.

## 1. Pick the stories (about 4 searches)

- Run `python3 tools/news_add.py --recent`. Skip stories already reviewed, unless something major and new has happened in them.
- Search the last 7 days of major news across these areas:
  - politics and protest;
  - the economy and markets;
  - technology and cyber security;
  - health;
  - disasters and climate;
  - science and society.

  For example, search "biggest news this week", "<month> <year> news", and one or two topic searches.
- Choose **at most 2 stories** that:
  - at least two major outlets report;
  - most adults would recognise;
  - you can state in one factual sentence (what, where, how big).
- Skip these stories, to match `docs/new-rhyme-spec.md`:
  - wars and battles still being fought;
  - terror attacks or mass killings from the last month;
  - crimes by named private people;
  - election campaigns and partisan fights;
  - celebrity news.

## 2. Find the rhyme (about 8 searches)

Name the pattern in one line: the mechanism, not the headline. For PHP2Shell that would be "a flaw in a lock everyone trusts, exposed in public", not "PHP bug". Then decide:

- **It echoes an existing rhyme.** Check `/tmp/pastforward-daily/rhymes.txt`. A story counts only if the rhyme's motif fits it as well as it fits that rhyme's own Then and Today. A journalist or historian should have drawn the comparison (find one), or the mechanism must be plainly the same. Write it as a news echo (below). Outcome: `echo`.
- **It follows a pattern the app lacks.** Trace the pattern back:
  - its seed, the oldest real case;
  - a famous case that could be the Then;
  - one to three echoes in between.

  If it could meet `docs/new-rhyme-spec.md`, log it with outcome `watch`. Give the `seed`, and a `note` that names the Then candidate, the echoes, and the source that draws the comparison. On a new-rhyme day, start there. Outcome: `watch`.
- **Neither.** Outcome `none`. It is still logged, so later runs do not check it again.

Verify every fact with web search, as in `docs/deep-echo-spec.md`.

## 3. Write and add

Write `/tmp/pastforward-daily/news.json`:

```
{
  "reviewed": [
    { "date": "2026-10-17", "story": "Student-led unrest sweeps France", "url": "https://...", "outcome": "echo", "rhyme": "commune" },
    { "date": "2026-10-21", "story": "PHP2Shell flaws expose most of the web", "url": "https://...", "outcome": "watch",
      "seed": "1851, Hobbs picks the ‘unpickable’ Bramah lock", "note": "Then: Heartbleed 2014. Echoes: Log4Shell 2021. Wiz and Rapid7 compare it to Log4Shell." }
  ],
  "echoes": {
    "commune": [
      { "year": 2026, "short": "France 2026", "title": "Student-led unrest sweeps France", "region": "europe",
        "line": "One sentence, max 22 words: what happened, one number, and why it fits the pattern.",
        "date": "2026-10-17", "source": "Al Jazeera", "url": "https://..." }
    ]
  },
  "closed": []
}
```

- **The news echo:**
  - **date:** the date of the report you cite, which must be in the last 10 days;
  - **year:** the year of that date;
  - **source:** the outlet;
  - **url:** a link to that report that opens. Prefer outlets without a paywall.
- At most 2 news echoes a day, and one per episode: do not add the same unrest again as it develops.
- **closed:** when a watch story is built into a rhyme, or judged not strong enough, list it here with a `result`.
- Run `python3 tools/news_add.py /tmp/pastforward-daily/news.json` and fix what it reports.

## How it shows in the app

- **On the home screen:** for 10 days after its date, the newest news echo makes the home open on its rhyme. A line above the rhyme reads "In the news · <title>". Tapping it shows every echo, back to the seed, with this one highlighted and a link to the report.
- **Afterwards:** it stays in the rhyme's chain as a dated echo.
- **When there is no fresh news:** the home opens on the Spanish flu.
