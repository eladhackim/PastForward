# More echoes: research spec

PastForward pairs a historical event (THEN) with a recent one (NOW) that follows the same pattern, then projects the next echo. Right now each pattern shows only those two real events. We want to show the full chain: other REAL events, at any time up to today, that clearly follow the same pattern. They can come before THEN, between THEN and NOW, or (rarely) after NOW.

Read your input file (a JSON array of rhymes; use each rhyme's "id", "theme", "then" and "now" to understand the pattern). For EACH rhyme, find 0 to 4 additional real echoes.

Quality bar (strict):
- Only events a historian or a well-read journalist would readily accept as the same pattern. Prefer famous, recognizable events.
- Never repeat the THEN or NOW event itself, and never include two events that are really the same episode.
- Spread them in time where possible (an ancient or early-modern case plus 20th-century ones is ideal).
- If there is no strong extra echo, return an empty list for that rhyme. Fewer good ones beat more weak ones.
- Facts must be right: verify the year and key facts with web search when you are not sure.
- Neutral wording on political topics.

Write a JSON object to /tmp/claude-0/-home-claude/4428d97e-2e11-54ef-9bab-ac8992a975f9/scratchpad/data/echoes-<GROUP>.json:

```
{
  "<rhyme id>": [
    {
      "year": 1957,                 // number; use a negative number for BC
      "short": "Asian Flu",         // card label, max 16 characters
      "title": "The 1957 Asian flu", // max 7 words
      "region": "world",            // one of: us, latam, europe, russia, mideast, africa, india, china, world
      "line": "One sentence, max 22 words: what happened and why it fits the pattern."
    }
  ]
}
```

Include every rhyme id from your input file as a key (use [] when there is none). Sort each list by year. Plain, direct language. No em dashes. Use curly quotes inside strings. Validate with: python3 -c "import json,sys; json.load(open(sys.argv[1]))" <file>. Reply with only the file path and a short list of anything you were unsure about.
