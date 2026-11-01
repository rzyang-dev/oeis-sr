import json, sys, re
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
cand = json.load(open(ROOT / "reports" / "closed_loop_candidates.json", encoding="utf-8"))
items = [("z1", a, 5, 1) for a in cand["z1"]] + [("deep", d["aid"], d["p"], d["r"]) for d in cand["deep"]]
seen = set(); uniq = []
for it in items:
    k = (it[1], it[2], it[3])
    if k not in seen:
        seen.add(k); uniq.append(it)
print("unique (aid,p,r):", len(uniq))

def bfile(aid, limit=1300):
    f = DATA / "files" / ("A" + aid[1:4]) / f"b{aid[1:]}.txt"
    if not f.exists(): return None
    v = {}
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        q = line.split()
        if len(q) >= 2:
            try: v[int(q[0])] = int(q[1])
            except ValueError: pass
        if len(v) >= limit: break
    return v

def raw(aid):
    f = DATA / "seq" / ("A" + aid[1:4]) / (aid + ".seq")
    return f.read_text(encoding="utf-8", errors="replace") if f.exists() else ""

def mentioned(txt, p):
    t = txt.lower()
    return bool(re.search(rf"mod(?:ulo)?\s*{p}\b", t) or re.search(rf"divisible by {p}\b", t)
                or (re.search(r"congruen", t) and re.search(rf"\b{p}\b", t)))

ok_list = []
for kind, aid, p, r in uniq:
    d = bfile(aid)
    if not d: continue
    cls = [x for n, x in d.items() if n % p == r]
    if len(cls) < 20: continue
    if all(x % p == 0 for x in cls) and not mentioned(raw(aid), p):
        ok_list.append({"kind": kind, "aid": aid, "p": p, "r": r, "pts": len(cls)})
print("verified + OEIS-text-silent:", len(ok_list))
import collections
print("by kind:", collections.Counter(x["kind"] for x in ok_list))
json.dump(ok_list, open(ROOT / "reports" / "closed_loop_verified.json", "w"), indent=1)
print("wrote closed_loop_verified.json")
