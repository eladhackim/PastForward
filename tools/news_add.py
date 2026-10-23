#!/usr/bin/env python3
"""Record the day's news review: echoes found in recent news, and stories to watch.

    python3 tools/news_add.py /tmp/pastforward-daily/news.json   # check, then add
    python3 tools/news_add.py --recent                         # stories reviewed in the last 14 days, and the watch list

The input (see docs/news-spec.md):
{
  "reviewed": [ { "date": "YYYY-MM-DD", "story": "...", "url": "https://...", "outcome": "echo" | "watch" | "none",
                  "rhyme": "<id, for echo>", "note": "...", "seed": "<oldest known case, for watch>" } ],
  "echoes": { "<rhyme id>": [ { echo as in docs/deep-echo-spec.md, plus "date", "source", "url" } ] },
  "closed": [ { "story": "<a watch story, exactly as logged>", "result": "added as rhyme <id>" | "not strong enough: ..." } ]
}
- Echoes are checked by tools/check_echoes.py, then must carry the report's date (the last 10 days), source and https link.
- They are added to this month's data/echoes-daily-YYYY-MM.json, where the app shows them as "In the news".
- Every reviewed story goes into data/news-log.json, so later runs skip it and new-rhyme days start from the watch list.
"""
import datetime, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
LOG = os.path.join(DATA, "news-log.json")
today = datetime.date.today()
log = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else []

if sys.argv[1:] == ["--recent"]:
    cut = (today - datetime.timedelta(days=14)).isoformat()
    print("Reviewed in the last 14 days (skip these unless something new happened):")
    for r in log:
        if r["reviewed"] >= cut:
            print(f"- {r['date']} {r['story']} -> {r['outcome']}{' ' + r['rhyme'] if r.get('rhyme') else ''}")
    watch = [r for r in log if r["outcome"] == "watch" and not r.get("closed")]
    print("\nWatch list (possible new rhymes; look here first on a new-rhyme day):")
    for r in watch:
        print(f"- {r['date']} {r['story']} | seed: {r.get('seed', '?')} | {r.get('note', '')}")
    if not watch: print("- (empty)")
    sys.exit(0)
if len(sys.argv) != 2:
    sys.exit(__doc__)

B = json.load(open(sys.argv[1], encoding="utf-8"))
errors = []
E = errors.append
recent = (today - datetime.timedelta(days=10)).isoformat()
day = lambda d: isinstance(d, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) and d <= today.isoformat()
url = lambda u: isinstance(u, str) and re.fullmatch(r"https://[^\s]+", u)

echoes = B.get("echoes") or {}
for rid, lst in echoes.items():
    for e in lst:
        tag = f"{rid} {e.get('short')}"
        if not day(e.get("date")) or e["date"] < recent: E(f"{tag}: date must be the report's date, within the last 10 days (YYYY-MM-DD)")
        elif e.get("year") != int(e["date"][:4]): E(f"{tag}: year must match the date")
        if not url(e.get("url")): E(f"{tag}: url must be an https link to the report")
        if not (isinstance(e.get("source"), str) and 2 <= len(e["source"]) <= 30): E(f"{tag}: source is the outlet's name, max 30 characters")
if echoes:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as t:
        json.dump(echoes, t, ensure_ascii=False)
    chk = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "check_echoes.py"), t.name], capture_output=True, text=True)
    os.unlink(t.name)
    print(chk.stdout.strip())
    if chk.returncode: E("check_echoes.py reported errors (above)")

reviewed = B.get("reviewed") or []
if not reviewed and not B.get("closed"): E("reviewed: list every story you looked at, even with outcome none")
seen = {(r["story"].lower(), r["date"]) for r in log}
for r in reviewed:
    tag = f"reviewed '{str(r.get('story'))[:40]}'"
    if not (isinstance(r.get("story"), str) and 3 <= len(r["story"].split()) <= 14): E(f"{tag}: story is 3 to 14 words")
    if not day(r.get("date")): E(f"{tag}: date YYYY-MM-DD")
    if not url(r.get("url")): E(f"{tag}: url must be an https link")
    if r.get("outcome") not in ("echo", "watch", "none"): E(f"{tag}: outcome is echo, watch or none")
    if r.get("outcome") == "echo" and r.get("rhyme") not in echoes: E(f"{tag}: an echo outcome names the rhyme its echo was added to")
    if r.get("outcome") == "watch" and not (r.get("seed") and r.get("note")): E(f"{tag}: a watch outcome needs the seed (oldest known case) and a note")
    if "—" in json.dumps(r, ensure_ascii=False): E(f"{tag}: em dash")

closed = B.get("closed") or []
open_watch = {r["story"] for r in log if r["outcome"] == "watch" and not r.get("closed")}
for c in closed:
    if c.get("story") not in open_watch: E(f"closed '{str(c.get('story'))[:40]}': not an open watch story (see --recent)")
    if not c.get("result"): E(f"closed '{str(c.get('story'))[:40]}': say what happened (result)")

if errors:
    print("\n".join("ERROR: " + e for e in errors)); sys.exit("stopped: nothing was added")

added = 0
if echoes:
    path = os.path.join(DATA, f"echoes-daily-{today:%Y-%m}.json")
    month = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    for rid, lst in echoes.items():
        cur = month.setdefault(rid, [])
        have = {(e["year"], e["short"]) for e in cur}
        for e in lst:
            if (e["year"], e["short"]) not in have: cur.append(e); have.add((e["year"], e["short"])); added += 1
        cur.sort(key=lambda e: e["year"])
    json.dump(dict(sorted(month.items())), open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for r in reviewed:
    if (r["story"].lower(), r["date"]) in seen: continue
    log.insert(0, {**{k: r[k] for k in ("date", "story", "url", "outcome") }, **{k: r[k] for k in ("rhyme", "seed", "note") if r.get(k)}, "reviewed": today.isoformat()})
for c in closed:
    for r in log:
        if r["outcome"] == "watch" and r["story"] == c["story"] and not r.get("closed"):
            r["closed"] = today.isoformat(); r["result"] = c["result"]
json.dump(log[:400], open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"added {added} news echo(es); logged {len(reviewed)} reviewed stor{'y' if len(reviewed) == 1 else 'ies'}")
