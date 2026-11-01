import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
def shift_dfa(B, k):
    kb = [int(x) for x in bin(k)[2:]][::-1]
    L = len(kb); states = {}
    def sid(s, carry, i):
        key = (s, carry, min(i, L)); states.setdefault(key, len(states)); return states[key]
    trans = {}; q = deque([(0, 0, 0)]); seen = {(0, 0, 0)}
    while q:
        s, carry, i = q.popleft(); cur = sid(s, carry, i)
        for d in (0, 1):
            b = kb[i] if i < L else 0
            t = d + b + carry; dp, cp = t & 1, t >> 1
            ns = B["trans"][s][dp]
            if ns < 0: trans[(cur, d)] = None; continue
            nxt = (ns, cp, min(i + 1, L))
            if nxt not in seen: seen.add(nxt); q.append(nxt)
            trans[(cur, d)] = sid(*nxt)
    out = {idx: (B["out"][B["trans"][s][1]] if carry else B["out"][s]) for (s, carry, i), idx in states.items()}
    n = len(states)
    return {"n": n, "out": [out[i] for i in range(n)],
            "trans": [[trans.get((i, d)) if trans.get((i, d)) is not None else -1 for d in (0, 1)] for i in range(n)]}
A = shift_dfa(m["A284948"], 1)
B = m["A096268"]
# BFS from (0,0) over x>=0, tracking digits (LSB first)
st = (0, 0)
seen = {st: ""}
q = deque([(st, "")])
witness = None
while q:
    (sa, sb), path = q.popleft()
    if A["out"][sa] != B["out"][sb]:
        x = int(path[::-1], 2) if path else 0
        witness = (x, A["out"][sa], B["out"][sb], path)
        break
    for d in (0, 1):
        ta, tb = A["trans"][sa][d], B["trans"][sb][d]
        if ta < 0 or tb < 0: continue
        if (ta, tb) not in seen:
            seen[(ta, tb)] = path + str(d)
            q.append(((ta, tb), path + str(d)))
x, va, vb, path = witness
n = x + 2
print("witness x =", x, " n =", n)
print("a(n) predicted:", va, " b(n-2) predicted:", vb)
from pathlib import Path
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
a = bfile("A284948"); b = bfile("A096268")
print("data a(n):", a.get(n), " data b(n-2):", b.get(n-2), " b-file max n:", max(a))
