import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000}
def shift_dfa(B, k):
    kb = [int(x) for x in bin(k)[2:]][::-1]
    L = len(kb)
    states = {}
    def sid(s, carry, i):
        key = (s, carry, min(i, L))
        if key not in states:
            states[key] = len(states)
        return states[key]
    trans = {}
    q = deque([(0, 0, 0)])
    seen = {(0, 0, 0)}
    while q:
        s, carry, i = q.popleft()
        cur = sid(s, carry, i)
        for d in (0, 1):
            b = kb[i] if i < L else 0
            t = d + b + carry
            dp, cp = t & 1, t >> 1
            ns = B["trans"][s][dp]
            if ns < 0:
                trans[(cur, d)] = None; continue
            nxt = (ns, cp, min(i + 1, L))
            if nxt not in seen:
                seen.add(nxt); q.append(nxt)
            trans[(cur, d)] = sid(*nxt)
    out = {}
    for (s, carry, i), idx in states.items():
        out[idx] = B["out"][B["trans"][s][1]] if carry else B["out"][s]
    n = len(states)
    return {"n": n, "out": [out[i] for i in range(n)],
            "trans": [[trans.get((i, d)) if trans.get((i, d)) is not None else -1 for d in (0, 1)] for i in range(n)]}
def decide(A, C, start_n=1):
    if start_n == 0:
        start = (0, 0)
    else:
        start = (A["trans"][0][1], C["trans"][0][1])
    if start[0] < 0 or start[1] < 0:
        return "undefined"
    seen = {start}; q = deque([start])
    while q:
        sa, sb = q.popleft()
        if A["out"][sa] != C["out"][sb]:
            return "mismatch"
        for d in (0, 1):
            ta, tb = A["trans"][sa][d], C["trans"][sb][d]
            if ta < 0 or tb < 0: continue
            if (ta, tb) not in seen:
                seen.add((ta, tb)); q.append((ta, tb))
    return "equal"
# A285383(n) = A035263(n-1) for n>=2  <=>  A285383(n+1) = A035263(n) for n>=1
C = shift_dfa(m["A285383"], 1)
print("A285383(n+1) = A035263(n) for n>=1? ->", decide(C, m["A035263"], 1))
# A284948(n) = A096268(n-2) for n>1  <=>  A284948(n+2) = A096268(n) for n>=0
C2 = shift_dfa(m["A284948"], 2)
print("A284948(n+2) = A096268(n) for n>=0? ->", decide(C2, m["A096268"], 0))
