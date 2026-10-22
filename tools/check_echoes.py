#!/usr/bin/env python3
"""Check echo research files before they go into the site.

    python3 tools/check_echoes.py data/echoes-<name>.json [...]

Errors (exit 1): unknown rhyme id, bad year, field over its limit, bad region, em dash, missing field.
Warnings: an echo within 2 years of Then, Today or an echo already in another file (often the same episode).
"""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
REG = {"us", "latam", "europe", "russia", "mideast", "africa", "india", "china", "world"}

pairs = {}
for f in sorted(glob.glob(os.path.join(DATA, "pairs-*.json"))):
    for p in json.load(open(f, encoding="utf-8")):
        pairs[p["id"]] = p

targets = [os.path.abspath(a) for a in sys.argv[1:]]
if not targets:
    sys.exit(__doc__)
others = {}
for f in sorted(glob.glob(os.path.join(DATA, "echoes-*.json"))):
    if os.path.abspath(f) in targets:
        continue
    for k, v in json.load(open(f, encoding="utf-8")).items():
        others.setdefault(k, []).extend(v)

errors, warns, total = [], [], 0
for f in targets:
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        errors.append(f"{f}: not valid JSON ({e})")
        continue
    for rid, lst in d.items():
        if rid not in pairs:
            errors.append(f"unknown rhyme id: {rid}")
            continue
        p = pairs[rid]
        years = [e.get("year") for e in lst]
        if years != sorted(y for y in years if isinstance(y, int)) and all(isinstance(y, int) for y in years):
            warns.append(f"{rid}: list not sorted by year")
        for e in lst:
            total += 1
            tag = f"{rid} {e.get('year')} {e.get('short')}"
            for k in ("year", "short", "title", "region", "line"):
                if k not in e or e[k] in ("", None):
                    errors.append(f"{tag}: missing {k}")
            y = e.get("year")
            if not isinstance(y, int) or y < -5000 or y > 2026:
                errors.append(f"{tag}: year must be a whole number between -5000 and 2026")
                continue
            if len(e.get("short", "")) > 16: errors.append(f"{tag}: short is over 16 characters")
            if len(e.get("title", "").split()) > 7: errors.append(f"{tag}: title is over 7 words")
            if len(e.get("line", "").split()) > 24: errors.append(f"{tag}: line is over 24 words")
            if e.get("region") not in REG: errors.append(f"{tag}: region must be one of {sorted(REG)}")
            if "—" in json.dumps(e, ensure_ascii=False): errors.append(f"{tag}: em dash")
            for k in ("then", "now"):
                if abs(y - p[k]["year"]) <= 2:
                    warns.append(f"{tag}: within 2 years of {k} ({p[k]['year']} {p[k]['short']})")
            for o in others.get(rid, []):
                if isinstance(o.get("year"), int) and abs(y - o["year"]) <= 2:
                    warns.append(f"{tag}: within 2 years of existing echo {o['year']} {o.get('short')}")

print(f"{total} echoes checked in {len(targets)} file(s)")
for w in warns: print("warning:", w)
for e in errors: print("ERROR:", e)
print("ok" if not errors else f"{len(errors)} error(s)")
sys.exit(1 if errors else 0)
