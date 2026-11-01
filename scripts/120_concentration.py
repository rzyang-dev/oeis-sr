import json, sys, csv
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
def bfile(aid, limit=5000):
    f = DATA/"files"/("A"+aid[1:4])/f"b{aid[1:]}.txt"
    if not f.exists(): return None
    d = {}
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line=line.strip()
        if not line or line.startswith("#"): continue
        q=line.split()
        if len(q)>=2:
            try: d[int(q[0])]=int(q[1])
            except ValueError: pass
        if len(d)>=limit: break
    return d or None
rows = json.load(open(ROOT/"reports"/"atlas930.json", encoding="utf-8"))
ok = [r for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000]
weak = []
stats = []
for r in ok:
    d = bfile(r["aid"], 3000)
    if not d: continue
    c = Counter(d.values())
    dom = c.most_common(1)[0][1]/len(d)
    stats.append((r["aid"], round(dom,3), len(c)))
    if dom > 0.9:
        weak.append((r["aid"], round(dom,3), len(c)))
print("entries:", len(stats), " near-constant (>90% one value):", len(weak))
for w in sorted(weak, key=lambda x:-x[1])[:15]:
    print("  ", w)
json.dump(stats, open(ROOT/"reports"/"value_concentration.json","w"))
