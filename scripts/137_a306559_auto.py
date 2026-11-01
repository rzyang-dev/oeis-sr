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
    out = {}
    for (s, carry, i), idx in states.items():
        ss, cc = s, carry
        for j in range(i, L):
            t = kb[j] + cc; ss = B["trans"][ss][t & 1]; cc = t >> 1
        if cc: ss = B["trans"][ss][1]
        out[idx] = B["out"][ss]
    n = len(states)
    return {"n": n, "out": [out[i] for i in range(n)],
            "trans": [[trans.get((i, d)) if trans.get((i, d)) is not None else -1 for d in (0, 1)] for i in range(n)]}
def decide(A, C, start=0):
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
# want a(n+5) = b(n); autA(x) = a(x+1), autB(n) = b(n)
C = shift_dfa(m["A306559"], 4)
print("A306559(n+5) = A039982(n)?", decide(C, m["A039982"], 0))
# also test the literal conjecture a(n+4)=b(n)
C2 = shift_dfa(m["A306559"], 3)
print("A306559(n+4) = A039982(n)?", decide(C2, m["A039982"], 0))
