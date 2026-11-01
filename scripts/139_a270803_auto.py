import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
def halve_dfa(B):
    """DFA for c(n) = B(floor((n+1)/2))."""
    states = {}
    def sid(s, carry, phase):
        key = (s, carry, phase); states.setdefault(key, len(states)); return states[key]
    trans = {}; q = deque([(0, 0, 0)]); seen = {(0, 0, 0)}
    while q:
        s, carry, phase = q.popleft(); cur = sid(s, carry, phase)
        for d in (0, 1):
            if phase == 0:
                nxt = (s, d, 1)
            else:
                t = d + carry
                b = t & 1; c2 = t >> 1
                ns = B["trans"][s][b]
                if ns < 0: trans[(cur, d)] = None; continue
                nxt = (ns, c2, 1)
            if nxt not in seen: seen.add(nxt); q.append(nxt)
            trans[(cur, d)] = sid(*nxt)
    out = {}
    for (s, carry, phase), idx in states.items():
        ss = B["trans"][s][carry] if (phase == 1) else B["trans"][s][0]
        out[idx] = B["out"][ss] if ss >= 0 else -1
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
C = halve_dfa(m["A151666"])
print("states:", C["n"])
print("A270803(n) = A151666(floor((n+1)/2)) for n>=1?", decide(m["A270803"], C, 1))
print("for n>=0?", decide(m["A270803"], C, 0))
