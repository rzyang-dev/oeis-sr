import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
for aid in ("A306559","A039982","A270803","A151666"):
    r = m.get(aid)
    print(aid, "shift", r["shift"] if r else None, "states", r["states"] if r else None)
DATA = Path(r"C:\Users\ginger\oeisdata")
def bfile(aid, limit=2000):
    f = DATA/"files"/("A"+aid[1:4])/f"b{aid[1:]}.txt"
    d = {}
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        line=line.strip()
        if not line or line.startswith("#"): continue
        q=line.split()
        if len(q)>=2:
            try: d[int(q[0])]=int(q[1])
            except ValueError: pass
        if len(d)>=limit: break
    return d
a = bfile("A306559"); b = bfile("A039982")
print("A306559 n=0..10:", [a.get(n) for n in range(11)])
print("A039982 n=0..10:", [b.get(n) for n in range(11)])
for k in range(0, 6):
    bad = [n for n in range(0, 500) if a.get(n+k) is not None and b.get(n) is not None and a[n+k] != b[n]]
    print(f"shift {k}: mismatches {len(bad)}", bad[:3])
