#!/usr/bin/env python3
"""Pick today's rhymes for the daily echo research and write the research input.

    python3 tools/daily_pick.py [N]      # default N = 3

Priority: rhymes with no echo before 1500 first, then the fewest echoes, then the longest since last researched.
Rhymes researched in the last 14 days are skipped while others remain.
Writes /tmp/pastforward-daily/input.json (today's rhymes) and rhymes.txt (every rhyme and the coverage gaps,
for finding a new one), and says whether today is a new-rhyme day (Mondays and Thursdays).
"""
import datetime, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = "/tmp/pastforward-daily"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3

pairs = []
for f in sorted(glob.glob(os.path.join(DATA, "pairs-*.json"))):
    pairs += json.load(open(f, encoding="utf-8"))
echoes = {}
for f in sorted(glob.glob(os.path.join(DATA, "echoes-*.json"))):
    for k, v in json.load(open(f, encoding="utf-8")).items():
        echoes.setdefault(k, []).extend(v)
log_path = os.path.join(DATA, "research-log.json")
log = json.load(open(log_path, encoding="utf-8")) if os.path.exists(log_path) else {}

today = datetime.date.today()
def days_since(rid):
    last = log.get(rid, {}).get("last")
    return (today - datetime.date.fromisoformat(last)).days if last else 10_000

def key(p):
    lst = echoes.get(p["id"], [])
    earliest = min([e["year"] for e in lst if isinstance(e.get("year"), int)] + [p["then"]["year"]])
    return (earliest >= 1500, len(lst), -days_since(p["id"]))

fresh = [p for p in pairs if days_since(p["id"]) >= 14]
# no echo before 1500 first, then fewest echoes, then longest since last researched
pool = sorted(fresh if len(fresh) >= N else pairs, key=lambda p: (not key(p)[0], key(p)[1], key(p)[2]))
chosen = pool[:N]

os.makedirs(OUT, exist_ok=True)
data = [{
    "id": p["id"], "theme": p["theme"],
    "then": {"year": p["then"]["year"], "title": p["then"]["title"]},
    "now": {"year": p["now"]["year"], "title": p["now"]["title"]},
    "older": p.get("older", ""),
    "already_listed": sorted([{"year": e["year"], "title": e["title"]} for e in echoes.get(p["id"], [])], key=lambda e: e["year"]),
} for p in chosen]
json.dump(data, open(os.path.join(OUT, "input.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# context for finding a new rhyme: every existing rhyme, and where the app is thin
world = {}
for f in sorted(glob.glob(os.path.join(DATA, "world-*.json"))):
    world.update(json.load(open(f, encoding="utf-8")))
from collections import Counter
reg = Counter(p[k]["region"] for p in pairs for k in ("then", "now"))
era = Counter("before 1700" if p["then"]["year"] < 1700 else "1700s" if p["then"]["year"] < 1800 else "1800s" if p["then"]["year"] < 1900 else "1900s" for p in pairs)
with open(os.path.join(OUT, "rhymes.txt"), "w", encoding="utf-8") as f:
    f.write(f"{len(pairs)} rhymes (id: Then -> Today, motif):\n")
    for p in sorted(pairs, key=lambda p: p["then"]["year"]):
        f.write(f"- {p['id']}: {p['then']['year']} {p['then']['title']} -> {p['now']['year']} {p['now']['title']} ({p['theme']})\n")
    f.write("\nRegions used by Then and Today events (lower = less covered): " + ", ".join(f"{r} {n}" for r, n in sorted(reg.items(), key=lambda x: x[1])) + "\n")
    f.write("Then eras: " + ", ".join(f"{e} {n}" for e, n in sorted(era.items(), key=lambda x: x[1])) + "\n")
    f.write("Years that already have world snapshots and headlines (no need to write them): " + ", ".join(sorted(world, key=int)) + "\n")
new_day = today.weekday() in (0, 3)   # Mondays and Thursdays: also look for one new rhyme
print(f"new-rhyme day: {'yes' if new_day else 'no'} (Mondays and Thursdays)")
print(f"wrote {OUT}/rhymes.txt")
for p in chosen:
    lst = echoes.get(p["id"], [])
    earliest = min([e["year"] for e in lst] + [p["then"]["year"]])
    print(f"{p['id']}: {len(lst) + 2} echoes, earliest {earliest}, last researched {log.get(p['id'], {}).get('last', 'never')}")
print(f"wrote {OUT}/input.json")
