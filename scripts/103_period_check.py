import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
ids = [a for a in json.load(open(ROOT/"reports"/"auto3_cand.json", encoding="utf-8"))]
atlas = set(a["aid"] for a in json.load(open(ROOT/"reports"/"atlas.json", encoding="utf-8")))
both = [a for a in ids if a in atlas]
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
def eventually_periodic(v, maxp=200, maxpre=500):
    n = len(v)
    for pre in range(0, min(maxpre, n//2)):
        for p in range(1, maxp+1):
            if n - pre < 3*p: continue
            if all(v[i] == v[i+p] for i in range(pre, n-p)):
                return (pre, p)
    return None
res = []
for aid in both:
    d = bfile(aid)
    if not d: continue
    v = [d[k] for k in sorted(d)]
    r = eventually_periodic(v)
    res.append((aid, r))
per = [x for x in res if x[1]]
print("both:", len(res), "eventually periodic (direct check):", len(per))
print("not eventually periodic:", len(res)-len(per))
for aid, r in res[:20]:
    print(f"  {aid} -> {r}")
