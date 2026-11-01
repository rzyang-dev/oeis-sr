import sys
from collections import deque
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
DATA = Path(r"C:\Users\ginger\oeisdata")
W, EMAX = 16, 9
def bfile(aid, limit=20000):
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
d = bfile("A014709")
def key_of(d, e, r):
    step = 1 << e
    vals = []
    for n in range(W):
        v = d.get(r + step*n)
        if v is None: return None
        vals.append(v)
    return tuple(vals)
ids = {}; out = {}
k0 = key_of(d, 0, 0)
ids[k0] = 0; out[0] = d[0]
q = deque([(0,0)]); trans = {}
while q:
    e, r = q.popleft()
    sid = ids[key_of(d, e, r)]
    for digit in (0,1):
        if e >= EMAX: trans[(sid,digit)] = None; continue
        rr = r + digit*(1<<e)
        kk = key_of(d, e+1, rr)
        if kk is None: trans[(sid,digit)] = None; continue
        if kk not in ids:
            ids[kk] = len(ids); out[ids[kk]] = d.get(rr); q.append((e+1, rr))
        trans[(sid,digit)] = ids[kk]
print("states:", len(ids), "complete:", all(v is not None for v in trans.values()))
for i in range(len(ids)):
    print("state", i, "out", out[i], "->0:", trans.get((i,0)), "->1:", trans.get((i,1)))
def predict(n):
    s = 0
    for ch in bin(n)[2:]:
        s = trans[(s, int(ch))]
        if s is None: return None
    return out[s]
for n in range(12):
    print(n, d.get(n), predict(n))
