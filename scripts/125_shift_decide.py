import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows if r["val_ok"] == r["val_total"] and r["val_total"] >= 1000}
def shift_dfa(B, k):
    """DFA for c(n) = B(n+k)."""
    kb = [int(x) for x in bin(k)[2:]][::-1]
    L = len(kb)
    states = {}
    def sid(s, carry, i):
        key = (s, carry, min(i, L))
        if key not in states:
            states[key] = len(states)
        return states[key]
    start = sid(0, 0, 0)
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
                trans[(cur, d)] = None
                continue
            nxt = (ns, cp, min(i + 1, L))
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
            trans[(cur, d)] = sid(*nxt)
    out = {}
    for (s, carry, i), idx in states.items():
        bb = B["out"][B["trans"][s][1]] if carry else B["out"][s]
        out[idx] = bb
    n = len(states)
    return {"n": n, "out": [out[i] for i in range(n)],
            "trans": [[trans.get((i, d)) if trans.get((i, d)) is not None else -1 for d in (0, 1)] for i in range(n)]}
def decide(A, C):
    start = (A["trans"][0][1], C["trans"][0][1])
    if start[0] < 0 or start[1] < 0:
        return "undefined"
    seen = {start}
    q = deque([start])
    while q:
        sa, sb = q.popleft()
        if A["out"][sa] != C["out"][sb]:
            return "mismatch"
        for d in (0, 1):
            ta, tb = A["trans"][sa][d], C["trans"][sb][d]
            if ta < 0 or tb < 0: continue
            if (ta, tb) not in seen:
                seen.add((ta, tb)); q.append((ta, tb))
    return "equal for all n>=1"
for a, b, k in (("A284948", "A096268", 2), ("A285383", "A035263", 1)):
    if a in m and b in m:
        C = shift_dfa(m[b], k)
        print(f"{a}(n) = {b}(n+{k})? -> {decide(m[a], C)}   (states {C['n']})")
    else:
        print(a, b, "missing")