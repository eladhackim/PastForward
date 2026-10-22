# Echo research: going deeper into the past

PastForward shows how history rhymes. Each **rhyme** is a recurring pattern with a **Then** event (historical) and a **Today** event (recent). Every real time the pattern happened is an **echo**. The app shows "Seen N times" with signal bars, so each verified echo makes a rhyme more convincing. Old echoes matter most: a pattern that also appears in Rome, Han China or medieval Venice feels like something deep about people, not a coincidence of our century.

## What to find

For each rhyme in your input:

1. **Deep past (priority).** Find 1 to 3 real echoes **before 1500**: antiquity, the classical world, ancient China and India, the Islamic golden age, medieval Europe, Africa and the Americas. Spread them out in time and place where you can.
2. **If there is no honest pre-1500 case**, find the oldest real one you can, even if it is 1500 to 1850. Some rhymes (a computer bug, a nuclear accident) have no ancient echo; an empty list is better than a forced one.
3. **The "older" note.** If the rhyme has an "older" field, write a full echo entry for that same event (verified, with a proper line), so it no longer shows as a bare title.

## Quality bar (strict)

- Only events a historian or a well-read journalist would readily accept as the same pattern. Name the mechanism that makes it rhyme in the line.
- Never repeat Then, Today, or anything in already_listed, and never add the same episode twice (same event within about 2 years).
- Verify every year and key fact with web search before including it. Ancient dates: use the year historians usually give; use a negative number for BC (431 BC = -431).
- Neutral wording on political and religious topics. No legends presented as fact; if a story is disputed (for example, it comes from one ancient author), either leave it out or say so in the line ("According to Suetonius, …").
- Plain, direct language. No em dashes, no hype, no rhetorical questions. Curly quotes inside strings.

## Output

A JSON object keyed by every rhyme id in your input (use `[]` when you add nothing), each list sorted by year:

```
{
  "<rhyme id>": [
    {
      "year": -431,                       // number; negative for BC
      "short": "Athens vs Sparta",        // card label, max 16 characters
      "title": "The Peloponnesian War begins", // max 7 words
      "region": "europe",                 // us, latam, europe, russia, mideast, africa, india, china, world
      "line": "One sentence, max 22 words: what happened and why it fits the pattern."
    }
  ]
}
```

Then run `python3 tools/check_echoes.py <your file>` from the repo root and fix everything it reports, except "near" warnings you have checked are separate events.
