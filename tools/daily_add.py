#!/usr/bin/env python3
"""Add a day's researched echoes to the site data, after checking them.

    python3 tools/daily_add.py /tmp/pastforward-daily/new.json

- Runs tools/check_echoes.py on the file; stops on any error.
- Merges the echoes into data/echoes-daily-YYYY-MM.json (this month's file), skipping exact repeats.
- Records every researched rhyme in data/research-log.json, even with nothing added, so the rotation moves on.
"""
import datetime, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
if len(sys.argv) != 2:
    sys.exit(__doc__)
src = os.path.abspath(sys.argv[1])
chk = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "check_echoes.py"), src], capture_output=True, text=True)
print(chk.stdout.strip())
if chk.returncode:
    sys.exit("stopped: fix the errors above, nothing was added")

new = json.load(open(src, encoding="utf-8"))
today = datetime.date.today()
month_path = os.path.join(DATA, f"echoes-daily-{today:%Y-%m}.json")
month = json.load(open(month_path, encoding="utf-8")) if os.path.exists(month_path) else {}
log_path = os.path.join(DATA, "research-log.json")
log = json.load(open(log_path, encoding="utf-8")) if os.path.exists(log_path) else {}

added = 0
for rid, lst in new.items():
    cur = month.setdefault(rid, [])
    seen = {(e["year"], e["short"]) for e in cur}
    n = 0
    for e in lst:
        if (e["year"], e["short"]) in seen:
            continue
        cur.append(e); seen.add((e["year"], e["short"])); n += 1
    cur.sort(key=lambda e: e["year"])
    if not cur:
        del month[rid]
    entry = log.setdefault(rid, {"runs": 0, "added": 0})
    entry["last"] = today.isoformat(); entry["runs"] += 1; entry["added"] += n
    added += n
    print(f"{rid}: +{n}")

if month:
    json.dump(dict(sorted(month.items())), open(month_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(dict(sorted(log.items())), open(log_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"added {added} echo(es)" + (f" to {os.path.relpath(month_path, ROOT)}" if added else ""))
