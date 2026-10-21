# History Rhymes: content spec

You are writing content for an interactive mobile web page called History Rhymes. It pairs a historical event (THEN) with a recent event that rhymes with it (NOW), and projects a possible future echo (NEXT) at year = NOW + (NOW - THEN). Example: Spanish flu 1918, then COVID-19 in 2020, so the next echo may come around 2122 (102 years later again). Readers are curious general adults on their phones. Today's date is 20 October 2026.

## FILE 1: pairs-<GROUP>.json

A JSON array, one object per pair in your list, in the same order, with exactly this shape:

```
{
  "id": "<given id>",
  "theme": "the shared pattern in 3-8 words, e.g. A pandemic in a hyper-connected world",
  "rhyme": 3,                       // 3 = strong, widely accepted parallel; 2 = partial; 1 = loose or contested
  "then": {
    "year": 1918,                   // number, as given
    "short": "Spanish Flu",         // label for a small card, max 14 characters
    "title": "The Spanish Flu",     // full name, max 6 words
    "where": "Worldwide",           // short place, e.g. "Paris, France"
    "region": "world",              // one of: us, latam, europe, russia, mideast, africa, india, china, world
    "hook": "one sentence, max 16 words, that makes the reader think: yes, I know that one",
    "text": "2-3 short sentences, max 55 words, concrete facts: what happened, numbers, names"
  },
  "now": {
    "year": 2020, "short": "...", "title": "...", "where": "...", "region": "...",
    "hook": "MUST start with 'Remember' and evoke a concrete moment the reader lived through, e.g. Remember spring 2020: empty streets, homemade bread, and life on video calls.",
    "text": "2-3 short sentences, max 55 words, concrete facts"
  },
  "followed": "1-2 sentences, max 40 words: what came after the THEN event last time (its aftermath or next turn)",
  "next": {
    "short": "card label for the future echo, max 14 characters",
    "title": "the possible future version of the pattern, max 7 words",
    "text": "1-2 sentences, max 40 words, imagining what this pattern might look like around the projected year. Use might/could. Plausible, grounded in the pattern, a little evocative.",
    "watch": "1 sentence, max 25 words: early signs to watch for in the coming decades"
  },
  "breaks": "1 sentence, max 30 words: the most important way the comparison does not hold",
  "older": "OPTIONAL: an earlier rhyme of the same pattern with its year, e.g. The Black Death, 1347. Omit the key if none is clear."
}
```

Region keys: us = United States; latam = Latin America and the Caribbean; europe = Europe incl. Britain; russia = Russia / Soviet Union; mideast = Middle East incl. Egypt, Turkey, Iran and North Africa; africa = sub-Saharan Africa; india = India and South Asia; china = China and East Asia incl. Japan and Korea; world = no single home.

## FILE 2: world-<GROUP>.json

An object keyed by year (string) for each year you are given, with a snapshot of the world in that specific year:

```
{ "1918": { "us": "...", "latam": "...", "europe": "...", "russia": "...", "mideast": "...", "africa": "...", "india": "...", "china": "..." } }
```

Each value: 1-2 sentences, max 32 words, about what was actually happening in that region in that specific year, not decade generalities. Name real events, rulers, wars, reforms, disasters, inventions, cultural moments. Describe the region as it was then: the British colonies before 1776, the Russian Empire or Soviet Union, the Ottoman Empire, British India, Qing China, colonial Africa, and so on. Japan and Korea go in "china"; Egypt and North Africa in "mideast"; "africa" is sub-Saharan Africa.

## Rules

- Accuracy matters more than color. Use only facts you are confident of, and check anything uncertain with web search. Dates and numbers must be right.
- Plain, direct language and short sentences. No em dashes. No "not X, but Y" constructions. No rhetorical questions. No hype words.
- Political topics: neutral and factual. Attribute contested views to the people who hold them. No partisan judgments.
- Valid JSON only. Inside strings use curly quotes (“ ” ‘ ’) rather than straight double quotes.
- Before finishing, validate each file: python3 -c "import json,sys; json.load(open(sys.argv[1]))" <file>
- Write files into /tmp/claude-0/-home-claude/4428d97e-2e11-54ef-9bab-ac8992a975f9/scratchpad/data/
- When done, reply only with the file paths and a short list of any facts you were unsure about.
