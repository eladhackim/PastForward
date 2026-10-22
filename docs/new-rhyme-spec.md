# Finding a new rhyme

PastForward pairs an event from history (**Then**) with a recent event that follows the same pattern (**Today**), and projects the **Next** at Today + (Today − Then). Example: the Spanish flu in 1918, COVID-19 in 2020, the next pandemic around 2122. Words used in the app are defined in the lexicon: rhyme, motif, echo, seed, match, cadence, Next.

A new rhyme is only worth adding if it is **as strong as the best ones already in the app**. Most days, the right answer is to add none.

## 1. Choose the rhyme

Read `/tmp/pastforward-daily/rhymes.txt` (every existing rhyme and the coverage gaps). Then look for a pattern that:

- **is real and widely recognised:** historians or serious journalists have drawn this comparison. Search for it and find at least one source that does.
- **has a Today the reader lived through:** a recent event (1990 or later, ideally 2005 or later) that most adults remember.
- **has a Then that is famous on its own:** the deeper in the past the better, if the match is genuinely close.
- **echoes at least 3 times in total,** including Then and Today. Find the other echoes too.
- **is new:** not a near-duplicate of an existing rhyme's motif, Then or Today.
- **fills a gap where possible:** an under-covered region (Africa, India, Latin America, China, the Middle East), an under-covered era (before 1700), or a theme the app lacks (science, culture, cities, food, sport, migration, religion, money).
- **lands its Next between 2027 and 2300.** Check: 2 × Today − Then.

Avoid topics that would mainly be painful or divisive without teaching anything: active wars, recent terror attacks, named private individuals, and anything partisan.

## 2. Write it

Write `/tmp/pastforward-daily/rhyme.json` with this shape. Every fact must be verified with web search.

```
{
  "pair": {
    "id": "short-lowercase-id",           // 2 to 20 letters, digits or dashes; not already used
    "theme": "The motif in 3 to 8 words",
    "rhyme": 2,                           // 3 = historians commonly draw it; 2 = alike in important ways; 1 = loose. Never add a 1.
    "then": {
      "year": 1666, "short": "Great Fire",            // short: max 14 characters
      "title": "The Great Fire of London",           // max 6 words
      "where": "London, England", "region": "europe", // regions below
      "hook": "One sentence, max 16 words, that makes the reader think: yes, I know that one.",
      "text": "2 or 3 short sentences, max 55 words: what happened, with numbers and names."
    },
    "now": {
      "year": 2019, "short": "Notre-Dame", "title": "...", "where": "...", "region": "...",
      "hook": "A plain, vivid fact about a moment the reader lived through, max 18 words. Do not start with “Remember”.",
      "text": "2 or 3 short sentences, max 55 words."
    },
    "followed": "1 or 2 sentences, max 40 words: what came after Then (its coda).",
    "next": {
      "short": "max 14 characters, no question mark",
      "title": "The likely next version, max 7 words, stated plainly, no question mark",
      "text": "1 or 2 sentences, max 40 words, imagining it around the projected year. Use might or could.",
      "watch": "1 sentence, max 25 words: the murmurs, early signs to watch for."
    },
    "breaks": "1 sentence, max 30 words: where the comparison stops working."
  },
  "echoes": [ /* 1 to 4 other real echoes, in the format of docs/deep-echo-spec.md */ ],
  "opportunities": {
    "lastTime": "1 or 2 sentences, max 45 words: who gained or what was in demand after Then. Real names.",
    "ideas": [
      { "kind": "build", "title": "max 6 words", "line": "max 24 words" },
      { "kind": "work",  "title": "...", "line": "..." },
      { "kind": "learn", "title": "...", "line": "..." }
    ],
    "watch": "1 sentence, max 25 words: the signal that the opportunity is opening."
  },
  "world": {
    "1666": { "us": "...", "latam": "...", "europe": "...", "russia": "...", "mideast": "...", "africa": "...", "india": "...", "china": "..." }
  },
  "headlines": {
    "1666": { "us": "max 30 characters", "latam": "...", "europe": "...", "russia": "...", "mideast": "...", "africa": "...", "india": "...", "china": "..." }
  }
}
```

- **world and headlines:** include them only for a Then or Today year the app does not have yet (`rhymes.txt` lists the covered years). Each world entry is 1 or 2 sentences, max 32 words, about what actually happened in that region in that exact year, describing the region as it was then (the Mughal Empire, Qing China, colonial Africa and so on). Each headline is the same event in max 30 characters.
- **Regions:** us = United States (or the land that became it); latam = Latin America and the Caribbean; europe = Europe including Britain; russia = Russia or the Soviet Union; mideast = Middle East including Egypt, Turkey, Iran and North Africa; africa = sub-Saharan Africa; india = South Asia; china = East Asia including Japan and Korea; world = no single home.
- **Openings:** this is a pattern lens, not financial or career advice. Never name stocks, coins or companies to invest in. For tragedies, focus on safety, recovery and public-interest work.
- **Style:** plain, direct, short sentences. No em dashes, no hype, no rhetorical questions. Neutral on politics and religion. Curly quotes inside strings.

## 3. Add it

`python3 tools/rhyme_add.py /tmp/pastforward-daily/rhyme.json` checks everything and adds the rhyme to the `*-daily` data files. Fix whatever it reports. If a problem cannot be fixed honestly, do not add the rhyme.
