# Opportunities: research spec

PastForward pairs a historical event (THEN) with a recent one (NOW) that follows the same pattern, and projects the next echo (NEXT). The new "Opportunities" layer answers a practical question: **last time this pattern played out, who gained and what was suddenly in demand, and what might that mean now?**

Read your input file (a JSON array of rhymes). Use each rhyme's `id`, `theme`, `then`, `now`, `followed` and `next` fields. You may also read `/home/claude/pastforward/data/echoes-*.json` for earlier occurrences of the same pattern.

For EACH rhyme, write:

```
"<rhyme id>": {
  "lastTime": "1-2 sentences, max 45 words. Concretely who gained or what was in demand after THEN (and its echoes): industries, products, jobs, skills, regions. Real, checkable facts with names.",
  "ideas": [
    { "kind": "build", "title": "max 6 words", "line": "max 24 words: a product, service, app or business area the pattern suggests could be in demand now or in the coming years." },
    { "kind": "work",  "title": "...", "line": "max 24 words: jobs or roles likely to grow." },
    { "kind": "learn", "title": "...", "line": "max 24 words: a skill or knowledge worth building." }
  ],
  "watch": "1 sentence, max 25 words: the signal that would show this opportunity is opening (or closing)."
}
```

- Give 3 or 4 ideas per rhyme, with at least one each of `build`, `work` and `learn`.
- Ideas must follow from the historical pattern. Say what is specific to this pattern, not generic advice ("learn AI" alone is too generic; "AI model auditing for regulated industries" is specific).
- Ground the ideas in today's world (2026). They should be plausible and concrete, and never sensational.
- This is a pattern lens, **not financial, investment or career advice**. Never name stocks, tickers, coins or specific companies to buy. Never promise returns. Use "may", "could" or "tends to".
- Political or tragic topics (wars, disasters, pandemics, persecution) need care: focus on resilience, recovery, protection, rebuilding, safety and public-interest work. Never suggest profiting from suffering.
- Accuracy: `lastTime` must be factually right. Check anything you are unsure of with web search.
- Plain, direct language. No em dashes, no hype words, no rhetorical questions. Use curly quotes inside strings.

Write a JSON object keyed by rhyme id, including every id in your input file, to `/home/claude/pastforward/data/opportunities-<GROUP>.json`. Validate it with `python3 -c "import json,sys; json.load(open(sys.argv[1]))" <file>`. Reply with only the file path and a short list of anything you were unsure about.
