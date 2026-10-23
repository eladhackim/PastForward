#!/usr/bin/env python3
"""Check a new rhyme and add it to the site data.

    python3 tools/rhyme_add.py /tmp/pastforward-daily/rhyme.json [--check]

Checks the shape, lengths, years, regions and style of the rhyme in docs/new-rhyme-spec.md, that it is new,
and that every year it uses has a world snapshot and headlines. With --check it only reports.
Otherwise it appends the rhyme (with today's date as "added") to data/pairs-daily.json and its
world, headlines, opportunities and echoes to the matching *-daily files.
"""
import datetime, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
REG = {"us", "latam", "europe", "russia", "mideast", "africa", "india", "china", "world"}
WREG = ["us", "latam", "europe", "russia", "mideast", "africa", "india", "china"]
args = [a for a in sys.argv[1:] if not a.startswith("--")]
if len(args) != 1:
    sys.exit(__doc__)
CHECK_ONLY = "--check" in sys.argv
B = json.load(open(args[0], encoding="utf-8"))
today = datetime.date.today()

def load_all(prefix, kind):
    out = [] if kind == "list" else {}
    for f in sorted(glob.glob(os.path.join(DATA, prefix + "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if kind == "list": out += d
        else: out.update(d)
    return out

pairs = load_all("pairs-", "list")
world = load_all("world-", "dict")
heads = load_all("headlines-", "dict")
errors, warns = [], []
E = errors.append
words = lambda s: len(str(s or "").split())

def style(where, s):
    s = str(s or "")
    if "—" in s: E(f"{where}: em dash")
    if "?" in s and where.startswith("next"): E(f"{where}: no question marks in the Next")
    if re.search(r'(?<![\w“])"', s): E(f"{where}: use curly quotes inside text")

p = B.get("pair") or {}
pid = p.get("id", "")
if not re.fullmatch(r"[a-z0-9-]{2,20}", pid): E("pair.id: 2 to 20 lowercase letters, digits or dashes")
if any(x["id"] == pid for x in pairs): E(f"pair.id: '{pid}' is already used")
missing = [k for k in ["theme", "rhyme", "then", "now", "followed", "next", "breaks"] if k not in p]
for k in missing: E(f"pair.{k}: missing")
if missing:
    print("\n".join("ERROR: " + e for e in errors)); sys.exit(1)

if not 3 <= words(p["theme"]) <= 8: E("pair.theme: 3 to 8 words")
if p["rhyme"] not in (2, 3): E("pair.rhyme: must be 2 or 3 (weak rhymes are not added)")
if p.get("topic") not in ("health", "money", "power", "tech", "disaster", "society"): E("pair.topic: one of health, money, power, tech, disaster, society")
for k in ("then", "now"):
    e = p[k]
    for f in ["year", "short", "title", "where", "region", "hook", "text"]:
        if not e.get(f) and e.get(f) != 0: E(f"pair.{k}.{f}: missing")
    if not isinstance(e.get("year"), int): E(f"pair.{k}.year: whole number"); continue
    if len(e.get("short", "")) > 14: E(f"pair.{k}.short: max 14 characters")
    if words(e.get("title")) > 6: E(f"pair.{k}.title: max 6 words")
    if words(e.get("hook")) > 18: E(f"pair.{k}.hook: max 18 words")
    if words(e.get("text")) > 60: E(f"pair.{k}.text: max 55 words")
    if e.get("region") not in REG: E(f"pair.{k}.region: one of {sorted(REG)}")
    for f in ("title", "hook", "text"): style(f"pair.{k}.{f}", e.get(f))
if str(p["now"].get("hook", "")).startswith("Remember"): E("pair.now.hook: do not start with “Remember”")
ty, ny = p["then"].get("year"), p["now"].get("year")
if isinstance(ty, int) and isinstance(ny, int):
    if not 1990 <= ny <= today.year: E(f"pair.now.year: Today must be between 1990 and {today.year}")
    if ty >= ny: E("pair.then.year must be before now.year")
    nx = 2 * ny - ty
    if not 2027 <= nx <= 2300: E(f"Next lands in {nx}; it must be between 2027 and 2300")
nxt = p["next"]
for f, n in (("short", None), ("title", 7), ("text", 45), ("watch", 27)):
    if not nxt.get(f): E(f"pair.next.{f}: missing")
    style(f"next.{f}", nxt.get(f))
if len(nxt.get("short", "")) > 14: E("pair.next.short: max 14 characters")
if words(nxt.get("title")) > 7: E("pair.next.title: max 7 words")
if words(p["followed"]) > 45: E("pair.followed: max 40 words")
if words(p["breaks"]) > 33: E("pair.breaks: max 30 words")
for f in ("theme", "followed", "breaks"): style(f"pair.{f}", p.get(f))

# is it new?
def norm(s): return re.sub(r"[^a-z0-9 ]", "", str(s).lower())
for x in pairs:
    for k in ("then", "now"):
        same_year = isinstance(p[k].get("year"), int) and abs(x[k]["year"] - p[k]["year"]) <= 1
        if same_year and (norm(x[k]["short"])[:6] == norm(p[k]["short"])[:6] or norm(x[k]["title"]) == norm(p[k]["title"])):
            E(f"pair.{k}: same event as existing rhyme '{x['id']}' ({x[k]['year']} {x[k]['short']})")
    if norm(x["theme"]) == norm(p["theme"]): E(f"pair.theme: same motif as existing rhyme '{x['id']}'")
    if abs(x["then"]["year"] - p["then"]["year"]) <= 3 and abs(x["now"]["year"] - p["now"]["year"]) <= 3:
        warns.append(f"close in time to existing rhyme '{x['id']}' ({x['then']['year']} → {x['now']['year']}): make sure it is a different pattern")

# world snapshots and headlines for any new year
W, H = B.get("world") or {}, B.get("headlines") or {}
for y in {p["then"].get("year"), p["now"].get("year")}:
    ys = str(y)
    if ys in world and ys in heads: continue
    w, h = W.get(ys) or {}, H.get(ys) or {}
    for r in WREG:
        if not w.get(r): E(f"world.{ys}.{r}: missing (the app has no snapshot for {ys} yet)")
        elif words(w[r]) > 36: E(f"world.{ys}.{r}: max 32 words")
        if not h.get(r): E(f"headlines.{ys}.{r}: missing")
        elif len(h[r]) > 30: E(f"headlines.{ys}.{r}: max 30 characters")
        style(f"world.{ys}.{r}", w.get(r)); style(f"headlines.{ys}.{r}", h.get(r))

# openings
o = B.get("opportunities") or {}
ideas = [i for i in o.get("ideas", []) if i.get("kind") in ("build", "work", "learn") and i.get("title") and i.get("line")]
if not o.get("lastTime") or len(ideas) < 3 or {i["kind"] for i in ideas} != {"build", "work", "learn"}:
    E("opportunities: needs lastTime and at least one build, work and learn idea")
for i in ideas:
    if words(i["title"]) > 6: E(f"opportunities idea '{i['title']}': title max 6 words")
    if words(i["line"]) > 26: E(f"opportunities idea '{i['title']}': line max 24 words")
    style("opportunities", i["title"] + " " + i["line"])

# echoes, checked with the same tool as daily echoes
ech = B.get("echoes") or []
if len([e for e in ech if isinstance(e, dict)]) < 1:
    E("echoes: add at least one other real echo, so the rhyme is seen 3 or more times")
if ech:
    for e in ech:
        tag = f"echo {e.get('year')} {e.get('short')}"
        if not isinstance(e.get("year"), int): E(f"{tag}: year must be a whole number"); continue
        if len(e.get("short", "")) > 16: E(f"{tag}: short max 16 characters")
        if words(e.get("title")) > 7: E(f"{tag}: title max 7 words")
        if words(e.get("line")) > 24: E(f"{tag}: line max 24 words")
        if e.get("region") not in REG: E(f"{tag}: region")
        if abs(e["year"] - ty) <= 2 or abs(e["year"] - ny) <= 2: warns.append(f"{tag}: within 2 years of Then or Today")
        style(tag, e.get("line"))

for w in warns: print("warning:", w)
for e in errors: print("ERROR:", e)
if errors:
    print(f"{len(errors)} error(s); nothing was added"); sys.exit(1)
if CHECK_ONLY:
    print("ok (check only)"); sys.exit(0)

def add_json(name, update):
    path = os.path.join(DATA, name)
    cur = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else ([] if name.startswith("pairs") else {})
    update(cur)
    json.dump(cur, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

p["added"] = today.isoformat()
add_json("pairs-daily.json", lambda cur: cur.append(p))
add_json("world-daily.json", lambda cur: cur.update({y: v for y, v in W.items() if y not in world}))
add_json("headlines-daily.json", lambda cur: cur.update({y: v for y, v in H.items() if y not in heads}))
add_json("opportunities-daily.json", lambda cur: cur.update({pid: {"lastTime": o["lastTime"], "ideas": ideas, "watch": o.get("watch", "")}}))
if ech:
    add_json(f"echoes-daily-{today:%Y-%m}.json", lambda cur: cur.update({pid: sorted(ech, key=lambda e: e["year"])}))
log_path = os.path.join(DATA, "research-log.json")
log = json.load(open(log_path, encoding="utf-8")) if os.path.exists(log_path) else {}
log[pid] = {"runs": 1, "added": len(ech), "last": today.isoformat(), "created": today.isoformat()}
json.dump(dict(sorted(log.items())), open(log_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"added rhyme '{pid}': {ty} {p['then']['short']} → {ny} {p['now']['short']} → c. {2 * ny - ty} {nxt['short']}, with {len(ech)} more echo(es)")
