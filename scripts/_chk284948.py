import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(r"C:\Users\ginger\oeisdata")
def bfile(aid, limit=1200):
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
A = bfile("A284948"); B = bfile("A096268")
print("A284948 n=0..15:", [A.get(n) for n in range(16)])
print("A096268 n=0..15:", [B.get(n) for n in range(16)])
bad = [n for n in range(2, min(max(A), max(B)+2)) if A.get(n) != B.get(n-2)]
print("data mismatches for a(n)=b(n-2), n>=2:", bad[:10], "count:", len(bad))
