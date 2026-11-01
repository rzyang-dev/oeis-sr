import json, sys
from collections import deque
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\ginger\Documents\oeis"
rows = json.load(open(ROOT + r"\reports\atlas930.json", encoding="utf-8"))
m = {r["aid"]: r for r in rows}
def reach_last1(A, B):
    """pairs reachable from (0,0) by a path whose last digit is 1"""
    start = (0, 0)
    R = {start}
    q = deque([start])
    while q:
        a, b = q.popleft()
        for d in (0, 1):
            na, nb = A["trans"][a][d], B["trans"][b][d]
            if na < 0 or nb < 0: continue
            if (na, nb) not in R:
                R.add((na, nb)); q.append((na, nb))
    R1 = set()
    for (a, b) in R:
        for d in (1,):
            na, nb = A["trans"][a][d], B["trans"][b][d]
            if na >= 0 and nb >= 0: R1.add((na, nb))
    return R, R1
for name, A, B in [("A267442~A043545", m["A267442"], m["A043545"]),
                   ("A285383~A035263(shift)", None, None)]:
    if A is None: continue
    R, R1 = reach_last1(A, B)
    bad = [(p, A["out"][p[0]], B["out"][p[1]]) for p in R1 if A["out"][p[0]] != B["out"][p[1]]]
    print(name, "R:", len(R), "R1:", sorted(R1), "bad:", bad)
# T4
X = m["A217586"]; Y = m["A096268"]; Z = m["A036987"]
states = {}
def sid(y, z):
    if (y, z) not in states: states[(y, z)] = len(states)
    return states[(y, z)]
q = deque([(0, 0)]); sid(0, 0)
trans = {}
while q:
    y, z = q.popleft()
    for d in (0, 1):
        ny, nz = Y["trans"][y][d], Z["trans"][z][d]
        if ny < 0 or nz < 0: trans[(sid(y,z), d)] = -1; continue
        if (ny, nz) not in states:
            states[(ny, nz)] = len(states); q.append((ny, nz))
        trans[(sid(y,z), d)] = sid(ny, nz)
n = len(states)
XOR = {"trans": [[trans.get((i,d), -1) for d in (0,1)] for i in range(n)],
       "out": [Y["out"][y] ^ Z["out"][z] for (y, z) in sorted(states, key=lambda k: states[k])]}
R, R1 = reach_last1(X, XOR)
bad = [(p, X["out"][p[0]], XOR["out"][p[1]]) for p in R1 if X["out"][p[0]] != XOR["out"][p[1]]]
print("A217586~XOR R:", len(R), "R1:", sorted(R1), "bad:", bad)
