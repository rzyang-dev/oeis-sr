import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
A = m["A285383"]; B = m["A035263"]
def shiftd(delta, s, d):
    c = s % 2
    t = (1 if d else 0) + c
    nb = delta["trans"][s // 2][t % 2]
    return nb * 2 + (t // 2)
s0 = 0 * 2 + 1
R = {(s0, 0)}
q = deque([(s0, 0)])
while q:
    s, b = q.popleft()
    for d in (0, 1):
        ns = shiftd(A, s, d); nb = B["trans"][b][d]
        if (ns, nb) not in R:
            R.add((ns, nb)); q.append((ns, nb))
print("ReachS:", sorted(R), "size", len(R))
def shiftout(delta, out, s):
    return out[delta["trans"][s // 2][1]] if s % 2 == 1 else out[s // 2]
bad = [(p, shiftout(A, A["out"], p[0]), B["out"][p[1]]) for p in R if shiftout(A, A["out"], p[0]) != B["out"][p[1]]]
print("bad:", bad)
