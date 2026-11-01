import json, sys
from fractions import Fraction
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
rows = json.load(open(ROOT/"reports"/"atlas_props.json", encoding="utf-8"))
def bfile(aid, limit=20000):
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
mismatch = []
checked = 0
for r in rows:
    d = bfile(r["aid"])
    if not d: continue
    v = list(d.values())
    emp = sum(1 for x in v if x == 0)/len(v)
    # empirical must match automaton density within tolerance
    if abs(emp - r["zero_density"]) > 0.01:
        mismatch.append((r["aid"], r["zero_density"], round(emp,4), r["states"], r["name"][:50]))
    checked += 1
print("checked:", checked, " mismatches:", len(mismatch))
for m in mismatch[:20]:
    print("  ", m)
# distribution of densities as fractions
from collections import Counter
c = Counter(Fraction(r["zero_density"]).limit_denominator(100) for r in rows)
print("density fractions:", c.most_common(12))
