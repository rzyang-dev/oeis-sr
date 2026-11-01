import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\ginger\Documents\oeis")
DATA = Path(r"C:\Users\ginger\oeisdata")
ids = json.load(open(ROOT/"reports"/"auto_strong.json", encoding="utf-8"))
def bfile(aid, limit=3000):
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
def kernel(d, p, W=10, MAXE=6):
    seen = set()
    nwin = 0
    for e in range(MAXE+1):
        mod = p**e
        for r in range(mod):
            w = []
            for k in range(W):
                idx = r + k*mod
                if idx not in d: w = None; break
                w.append(d[idx])
            if w is not None:
                nwin += 1
                if any(w):
                    seen.add(tuple(w))
    return len(seen), nwin
import sqlite3
con = sqlite3.connect("file:" + (ROOT/"oeis.db").as_posix() + "?mode=ro", uri=True)
names = dict(con.execute("select aid, name from seq"))
strong = []
for aid in ids:
    d = bfile(aid)
    if not d or max(d) < 512: continue
    k2, nw2 = kernel(d, 2)
    k3, nw3 = kernel(d, 3)
    if nw2 < 100:
        continue
    if k2 <= 30 and k2 > 0:
        strong.append((aid, k2, k3))
print("strict candidates:", len(strong))
for aid, k2, k3 in sorted(strong, key=lambda x: x[1])[:30]:
    print(f"  {aid} k2={k2} k3={k3} | {names.get(aid,'')[:66]}")
json.dump(strong, open(ROOT/"reports"/"auto_strict.json","w"), indent=1)