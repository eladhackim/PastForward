#!/usr/bin/env python3
"""Build PastForward: merge src/template.html with the content in data/ into index.html.

    python3 tools/build.py                  # writes index.html (the deployed site)
    python3 tools/build.py --body out.html  # also writes a body-only copy (no <html>/<head> wrapper), for previews

The site is one static file with everything embedded. Do not edit index.html by hand.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SRC = os.path.join(ROOT, "src", "template.html")
OUT = os.path.join(ROOT, "index.html")

REG = {"us", "latam", "europe", "russia", "mideast", "africa", "india", "china", "world"}
WREG = ["us", "latam", "europe", "russia", "mideast", "africa", "india", "china"]


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def files(prefix):
    return sorted(n for n in os.listdir(DATA) if n.startswith(prefix) and n.endswith(".json"))


pairs, world, heads, echoes, problems = [], {}, {}, {}, []
for n in files("pairs-"): pairs += load(n)
for n in files("world-"): world.update(load(n))
for n in files("headlines-"): heads.update(load(n))
for n in files("echoes-"): echoes.update(load(n))
MAP = load("map.json")

# ---- checks ----
ids = set()
def no_em_dash(where, s):
    if "—" in (s or ""): problems.append(f"em dash in {where}")
for p in pairs:
    pid = p.get("id", "?")
    if pid in ids: problems.append(f"duplicate id {pid}")
    ids.add(pid)
    for k in ["id", "theme", "rhyme", "then", "now", "followed", "next", "breaks"]:
        if k not in p: problems.append(f"{pid}: missing {k}")
    if p.get("rhyme") not in (1, 2, 3): problems.append(f"{pid}: rhyme must be 1, 2 or 3")
    for k in ["then", "now"]:
        e = p[k]
        for f in ["year", "short", "title", "where", "region", "hook", "text"]:
            if f not in e: problems.append(f"{pid}.{k}: missing {f}")
        if e.get("region") not in REG: problems.append(f"{pid}.{k}: unknown region {e.get('region')}")
        if str(e["year"]) not in world: problems.append(f"{pid}.{k}: no world snapshot for {e['year']}")
        for f in ["hook", "text", "title"]: no_em_dash(f"{pid}.{k}.{f}", e.get(f))
    for f in ["short", "title", "text", "watch"]:
        if f not in p["next"]: problems.append(f"{pid}.next: missing {f}")
        no_em_dash(f"{pid}.next.{f}", p["next"].get(f))
    ny = 2 * p["now"]["year"] - p["then"]["year"]
    if not (2027 <= ny <= 2300): problems.append(f"{pid}: next year {ny} out of range")
for y, w in world.items():
    for r in WREG:
        if not w.get(r): problems.append(f"world {y}: missing {r}")
        if not heads.get(y, {}).get(r): problems.append(f"headline {y}: missing {r}")

# ---- echoes: researched chains plus each rhyme's "older" rhyme ----
for p in pairs:
    lst = [dict(e) for e in echoes.get(p["id"], []) if isinstance(e.get("year"), int)]
    if p.get("older"):
        m = re.match(r"^(.*?),\s*(?:c\.\s*)?(\d{1,4})(\s*BC)?\s*$", p["older"].strip())
        if m:
            yr = int(m.group(2)) * (-1 if m.group(3) else 1)
            title = m.group(1).strip()
            if all(abs(e["year"] - yr) > 2 for e in lst):
                short = re.sub(r"^The ", "", title)
                lst.append({"year": yr, "short": short if len(short) <= 16 else short[:15].rstrip() + "…",
                            "title": title, "region": "world", "line": ""})
    keep = []
    for e in sorted(lst, key=lambda e: e["year"]):
        same = lambda k: abs(e["year"] - p[k]["year"]) <= 1 and e["short"].lower()[:5] == p[k]["short"].lower()[:5]
        if same("then") or same("now"): continue
        if e.get("region") not in REG: e["region"] = "world"
        keep.append(e)
    p["echoes"] = keep

# ---- "Today" lines read as plain facts, not prompts to the reader ----
OVERRIDE = {
    "transistor": "Late 2022: millions type their first question into ChatGPT, built on a 2017 Google idea.",
    "martians": "March 2023: the Pope in a stylish white puffer jacket, later revealed as AI-made.",
}
for p in pairs:
    h = p["now"]["hook"]
    if h.startswith("Remember "):
        h = h[len("Remember "):]
        h = h[0].upper() + h[1:]
    p["now"]["hook"] = OVERRIDE.get(p["id"], h)


def js(o):
    return json.dumps(o, ensure_ascii=False).replace("</", "<\\/")


with open(SRC, encoding="utf-8") as f:
    body = f.read()
body = (body.replace("/*__HEAD__*/{}", js(heads))
            .replace("/*__PAIRS__*/[]", js(pairs))
            .replace("/*__WORLD__*/{}", js(world))
            .replace('/*__MAP__*/{ cols: 1, rows: 1, grid: ".", pins: {} }', js(MAP)))
for token in ["/*__HEAD__*/", "/*__PAIRS__*/", "/*__WORLD__*/", "/*__MAP__*/"]:
    if token in body: problems.append(f"placeholder {token} was not filled")

ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230C0A1D'/%3E"
        "%3Cpath d='M10 44 Q21 18 32 40 Q43 62 54 22' fill='none' stroke='%23CDB9FF' stroke-width='4' stroke-linecap='round'/%3E"
        "%3Ccircle cx='10' cy='44' r='5' fill='%23E2B35E'/%3E%3Ccircle cx='32' cy='40' r='5' fill='%2372D3C5'/%3E%3Ccircle cx='54' cy='22' r='6' fill='%23CDB9FF'/%3E%3C/svg%3E")
HEAD_HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>PastForward</title>
<meta name="description" content="History rhymes. Swipe through 550 years, follow each event to its echo today, and see where the pattern may return. Find the echoes due in your own lifetime.">
<meta name="theme-color" content="#0C0A1D">
<meta property="og:title" content="PastForward">
<meta property="og:description" content="1918 → 2020 → 2122. History rhymes. What will you live to see?">
<meta property="og:type" content="website">
<meta property="og:url" content="https://pastforward.app/">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{ICON}">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);box-sizing:border-box;height:100%}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
"""
site = body.replace("<title>PastForward</title>\n", "").replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HEAD_HTML + site + "\n</html>\n")

if "--body" in sys.argv:
    with open(sys.argv[sys.argv.index("--body") + 1], "w", encoding="utf-8") as f:
        f.write(body)

print(f"{len(pairs)} rhymes · {sum(len(p['echoes']) for p in pairs)} extra echoes · {len(world)} world years")
print("\n".join(problems) if problems else "checks passed")
print(f"wrote index.html ({os.path.getsize(OUT) // 1024} KB)")
sys.exit(1 if problems else 0)
