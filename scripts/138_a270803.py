import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
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
A = bfile("A270803"); B = bfile("A151666")
print("A270803 n=0..10:", [A.get(n) for n in range(11)])
print("A151666 n=0..10:", [B.get(n) for n in range(11)])
for form, f in [("floor((n+1)/2)", lambda n: (n+1)//2), ("floor(n/2)", lambda n: n//2), ("n", lambda n: n)]:
    bad = [n for n in range(0, 500) if A.get(n) is not None and B.get(f(n)) is not None and A[n] != B[f(n)]]
    print(f"a(n) = b({form}): mismatches {len(bad)}", bad[:3])
