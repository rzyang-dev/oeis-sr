import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
A = m["A270803"]; B = m["A151666"]
def shiftd(trans, s, d):
    c = s % 2
    t = (1 if d else 0) + c
    return trans(s // 2, t % 2) * 2 + (t // 2)
def halveD(delta_trans, s, d):
    if s % 2 == 0:
        return (s // 4) * 4 + (1 if d else 0) * 2 + 1
    t = shiftd(delta_trans, (s // 4) * 2 + (s // 2) % 2, d)
    return 2 * t + 1
t0 = lambda b, d: B["trans"][b][1 if d else 0]
R = {(0,0)}; q = deque([(0,0)])
while q:
    a, h = q.popleft()
    for d in (0,1):
        na = A["trans"][a][d]; nh = halveD(t0, h, d)
        if (na,nh) not in R:
            R.add((na,nh)); q.append((na,nh))
print("R:", sorted(R))
