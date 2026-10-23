#!/usr/bin/env python3
"""Check guide files: the what, why and how behind each Opening idea.

    python3 tools/check_guides.py data/guides-A.json [more files]

A guide file maps rhyme id -> idea title (exactly as in data/opportunities-*.json) -> guide:
    {"what": "...", "why": "...", "how": ["...", "...", "..."], "read": [{"title": "...", "url": "https://..."}]}
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
opps = {}
for f in sorted(glob.glob(os.path.join(ROOT, "data", "opportunities-*.json"))):
    opps.update(json.load(open(f, encoding="utf-8")))
words = lambda s: len(str(s or "").split())
errors, count = [], 0


def style(where, s):
    s = str(s or "")
    if "—" in s: errors.append(f"{where}: em dash")
    if re.search(r"\bwill\b", s, re.I): errors.append(f"{where}: say may or could, not will")
    if re.search(r"(?<![\w“])\"", s): errors.append(f"{where}: use curly quotes inside text")


for path in sys.argv[1:]:
    data = json.load(open(path, encoding="utf-8"))
    for rid, by_title in data.items():
        if rid not in opps: errors.append(f"{path}: unknown rhyme '{rid}'"); continue
        titles = {i["title"] for i in opps[rid]["ideas"]}
        for title, g in by_title.items():
            where = f"{rid} / {title}"
            if title not in titles: errors.append(f"{where}: no idea with this exact title"); continue
            count += 1
            for f, n in (("what", 38), ("why", 44)):
                if not g.get(f): errors.append(f"{where}: missing {f}")
                elif words(g[f]) > n: errors.append(f"{where}: {f} has {words(g[f])} words (max {n})")
                style(f"{where}.{f}", g.get(f))
            how = g.get("how")
            if not isinstance(how, list) or not 2 <= len(how) <= 4: errors.append(f"{where}: how needs 2 to 4 steps")
            else:
                for k, step in enumerate(how):
                    if words(step) > 20: errors.append(f"{where}: how step {k + 1} has {words(step)} words (max 20)")
                    style(f"{where}.how[{k}]", step)
            for r in g.get("read", []) or []:
                if not (isinstance(r, dict) and r.get("title") and re.match(r"^https://[^\s]+$", str(r.get("url", "")))):
                    errors.append(f"{where}: each read item needs a title and an https url")
            if len(g.get("read", []) or []) > 2: errors.append(f"{where}: at most 2 read items")
for e in errors: print("ERROR:", e)
print(f"{count} guides checked, {len(errors)} problem(s)")
sys.exit(1 if errors else 0)
