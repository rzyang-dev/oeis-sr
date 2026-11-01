import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
A = m["A306559"]; B = m["A039982"]
def shiftd(trans, s, d):
    c = s % 2
    t = (1 if d else 0) + c
    return trans(s // 2, t % 2) * 2 + (t // 2)
def shiftout(trans, out, s):
    return out(trans(s // 2, True)) if s % 2 == 1 else out(s // 2)
t = lambda b, d: A["trans"][b][1 if d else 0]
o = lambda b: A["out"][b]
start = 1
for level in range(4):
    t_old, o_old = t, o
    t = lambda s, d, t_old=t_old: shiftd(t_old, s, d)
    o = lambda s, o_old=o_old, t_old=t_old: shiftout(t_old, o_old, s)
    if level > 0:
        start = start * 2 + 1
# reachable product pairs (t-state, B-state) from (start, 0)
R = {(start, 0)}
q = deque([(start, 0)])
while q:
    s, b = q.popleft()
    for d in (0, 1):
        ns = t(s, d); nb = B["trans"][b][d]
        if (ns, nb) not in R:
            R.add((ns, nb)); q.append((ns, nb))
print("product size:", len(R))
bad = [(p, o(p[0]), B["out"][p[1]]) for p in R if o(p[0]) != B["out"][p[1]]]
print("bad:", len(bad), bad[:5])
print("max state:", max(p[0] for p in R))
