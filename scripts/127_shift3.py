import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
def shift_dfa(B, k):
    kb = [int(x) for x in bin(k)[2:]][::-1]
    L = len(kb)
    states = {}
    def sid(s, carry, i):
        key = (s, carry, min(i, L))
        states.setdefault(key, len(states))
        return states[key]
    trans = {}
    q = deque([(0, 0, 0)]); seen = {(0, 0, 0)}
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
def decide(A, C, start=1):
    st = (A["trans"][0][1], C["trans"][0][1]) if start else (0, 0)
    seen = {st}; q = deque([st])
    while q:
        sa, sb = q.popleft()
        if A["out"][sa] != C["out"][sb]: return "mismatch"
        for d in (0, 1):
            ta, tb = A["trans"][sa][d], C["trans"][sb][d]
            if ta < 0 or tb < 0: continue
            if (ta, tb) not in seen: seen.add((ta, tb)); q.append((ta, tb))
    return "equal"
# A284948 shift 1, A096268 shift 0.  Want a(n)=b(n-2), n>=2  <=> A_autom(x+1)=B_autom(x), x>=0
print("A284948(n)=A096268(n-2), n>=2 ->", decide(shift_dfa(m["A284948"], 1), m["A096268"], 0))
# A285383 shift 1, A035263 shift 1.  Want a(n)=b(n-1), n>=2 <=> A_autom(x)=B_autom(x-1), x>=1
# equivalently B_autom(x-1) shifted: compare A_autom(x) with B_autom(x-1) via data check at small n
A = m["A285383"]; B = m["A035263"]
def val(D, n):
    s = 0
    for ch in reversed(bin(n)[2:]):
        s = D["trans"][s][int(ch)]
        if s < 0: return None
    return D["out"][s]
print("a(2),b(1) via automata:", val(A,1), val(B,0), " (a(n)=A_autom(n-1), b(n)=B_autom(n-1))")
