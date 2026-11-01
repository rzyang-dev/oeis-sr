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
t = lambda b, d: A["trans"][b][1 if d else 0]
start = 1
for level in range(4):
    t_old = t
    t = lambda s, d, t_old=t_old: shiftd(t_old, s, d)
    if level > 0:
        start = start * 2 + 1
R = {(start, 0)}
q = deque([(start, 0)])
while q:
    s, b = q.popleft()
    for d in (0, 1):
        ns = t(s, d); nb = B["trans"][b][d]
        if (ns, nb) not in R:
            R.add((ns, nb)); q.append((ns, nb))
print(sorted(R))
